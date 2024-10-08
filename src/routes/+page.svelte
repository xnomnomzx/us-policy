<script>
  import { onMount } from 'svelte';
  import { X, Send } from 'lucide-svelte'; // Importing icons
  import DOMPurify from 'dompurify';
  import { fade } from 'svelte/transition';

  let documents = [];
  let selectedDocument = null;
  let question = '';
  let isLoading = false;
  let showLandingPage = true;
  let messages = [];
  let chatContainer;

  // State variables for the page note
  let showPageNote = null; // Initialize as null to prevent flash
  let dontShowAgain = false;

  const CACHE_DURATION = 3600 * 1000; // 1 hour in milliseconds

  onMount(async () => {
    await fetchDocuments();
    cleanUpCache();
    const interval = setInterval(cleanUpCache, CACHE_DURATION);
    return () => clearInterval(interval);
  });

  // Load the dismissal state from LocalStorage
  onMount(() => {
    const dismissed = localStorage.getItem('dismissPageNote');
    if (dismissed === 'true') {
      showPageNote = false;
    } else {
      showPageNote = true;
    }
  });

  // Function to handle dismissal of the page note
  function dismissPageNote() {
    console.log('Dismiss button clicked'); // Debugging statement
    showPageNote = false;
    if (dontShowAgain) {
      localStorage.setItem('dismissPageNote', 'true');
    }
  }

  async function fetchDocuments() {
    try {
      const response = await fetch(
        'https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/documents',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      if (!response.ok) {
        throw new Error(`Failed to fetch documents: ${response.status} ${response.statusText}`);
      }
      documents = await response.json();
      console.log('Documents:', documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  }

  function selectDocument(id) {
    if (selectedDocument && selectedDocument.id === id) {
      // Same document selected, do nothing
      return;
    }
    selectedDocument = documents.find((doc) => doc.id === id);
    console.log('Selected document:', selectedDocument);
    question = '';
    showLandingPage = false;
    messages = [];
  }

  // Helper function to generate a unique cache key
  function generateCacheKey(documentId, question) {
    return `${documentId}::${question}`;
  }

  // Helper function to retrieve cached response
  function getCachedResponse(documentId, question) {
    const cacheKey = generateCacheKey(documentId, question);
    const cachedData = localStorage.getItem(cacheKey);
    if (cachedData) {
      const { response, timestamp } = JSON.parse(cachedData);
      if (Date.now() - timestamp < CACHE_DURATION) {
        return response;
      } else {
        // Cache expired
        localStorage.removeItem(cacheKey);
        console.log('Cache expired for key:', cacheKey);
      }
    }
    return null;
  }

  // Helper function to cache response
  function cacheResponse(documentId, question, response) {
    const cacheKey = generateCacheKey(documentId, question);
    const cacheEntry = {
      response,
      timestamp: Date.now()
    };
    localStorage.setItem(cacheKey, JSON.stringify(cacheEntry));
    console.log('Cached response for key:', cacheKey);
  }

  // Function to process citations in the assistant's response
  function processCitations(responseText) {
    const source_url = selectedDocument.source_url; // Get the source URL

    function replacePageNumbers(match, pageNumbersStr) {
      const pageNumbers = pageNumbersStr.split(',').map((p) => p.trim());
      const links = pageNumbers.map(
        (page) => `<a href="${source_url}#page=${page}">Page ${page}</a>`
      );
      return '(' + links.join(', ') + ')';
    }

    // Regex pattern to match your citation format '%&(Pg.#)'
    const regex = /%&\(Pg\.([\d,]+)\)/g;

    // Replace citations in the response text
    const processedText = responseText.replace(regex, replacePageNumbers);

    return processedText;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (question.trim()) {
      if (!selectedDocument) {
        console.error('No document selected.');
        return;
      }

      const userQuestion = question.trim();
      isLoading = true;
      messages = [...messages, { type: 'user', text: userQuestion }];
      question = '';
      console.log('Messages after user input:', messages);

      // Retrieve cached response based on document and question
      const cachedResponse = getCachedResponse(selectedDocument.id, userQuestion);
      if (cachedResponse) {
        messages = [
          ...messages,
          {
            type: 'bot',
            text: cachedResponse,
            displayedText: '',
            typing: true
          }
        ];
        console.log('Retrieved response from cache:', cachedResponse);
        isLoading = false;

        // Start the typing effect
        typeAssistantMessage(messages[messages.length - 1]);

        return;
      }

      try {
        const response = await fetch(
          'https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/chat',
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              message: userQuestion,
              documentId: selectedDocument.id,
              source_url: selectedDocument.source_url // Pass source_url to the backend
            })
          }
        );

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers.get('Content-Type'));

        // Check if the response is JSON
        const contentType = response.headers.get('Content-Type');
        if (!contentType || !contentType.includes('application/json')) {
          const text = await response.text();
          console.error('Non-JSON response received:', text);
          throw new Error('Invalid JSON response from the API');
        }

        const data = await response.json();
        console.log('Received data:', data);

        // Process the assistant's response
        const processedResponse = processCitations(data.response);

        // Cache the processed response
        cacheResponse(selectedDocument.id, userQuestion, processedResponse);

        // Prepare the assistant's message
        const assistantMessage = {
          type: 'bot',
          text: processedResponse,
          displayedText: '', // For typing effect
          typing: true
        };

        // Add the assistant's message to messages
        messages = [...messages, assistantMessage];
        console.log('Messages after bot response:', messages);

        // Start the typing effect
        typeAssistantMessage(assistantMessage);

      } catch (error) {
        console.error('Error fetching answer:', error);
        messages = [
          ...messages,
          {
            type: 'bot',
            text: 'Sorry, there was an error fetching the answer. Please try again.',
            displayedText: 'Sorry, there was an error fetching the answer. Please try again.',
            typing: false
          }
        ];
        scrollToBottom();
      } finally {
        isLoading = false;
      }
    }
  }

  function parseAssistantResponse(htmlContent) {
    // Sanitize the HTML content using DOMPurify
    const sanitizedContent = DOMPurify.sanitize(htmlContent);
    // Return the sanitized HTML content
    return sanitizedContent;
  }

  function typeAssistantMessage(message) {
    const fullText = message.text;
    let index = 0;
    const typingSpeed = 10; // milliseconds per character

    function typeCharacter() {
      if (index < fullText.length) {
        if (fullText[index] === '<') {
          // Detect the start of an HTML tag
          const endTagIndex = fullText.indexOf('>', index);
          if (endTagIndex !== -1) {
            // Append the entire tag at once
            message.displayedText += fullText.slice(index, endTagIndex + 1);
            index = endTagIndex + 1;
          } else {
            // Malformed tag; append the character and continue
            message.displayedText += fullText[index];
            index++;
          }
        } else {
          // Append the next character
          message.displayedText += fullText[index];
          index++;
        }

        // Update the messages array to trigger reactivity
        messages = [...messages];

        // Scroll to bottom after updating messages
        scrollToBottom();

        // Schedule the next character
        setTimeout(typeCharacter, typingSpeed);
      } else {
        // Typing finished
        message.typing = false;
        messages = [...messages];
      }
    }

    typeCharacter();
  }

  function scrollToBottom() {
    setTimeout(() => {
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 0);
  }

  function cleanUpCache() {
    const now = Date.now();

    for (const key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        // Expecting keys in the format 'documentId::question'
        if (key.includes('::')) {
          const cachedData = localStorage.getItem(key);
          if (cachedData) {
            const { timestamp } = JSON.parse(cachedData);
            if (now - timestamp > CACHE_DURATION) {
              localStorage.removeItem(key);
              console.log('Removed expired cache for key:', key);
            }
          }
        }
      }
    }
  }
</script>

<div class="h-screen bg-gray-900 flex flex-col">
  <!-- Header -->
  <header class="bg-gray-800 text-gray-100 p-4 flex-shrink-0">
    <div class="flex items-center">
      <h1 class="text-3xl font-bold">UsPolicy.io</h1>
      {#if selectedDocument}
        <h2 class="text-xl ml-4">{selectedDocument.title}</h2>
      {/if}
    </div>
  </header>

  <div class="flex flex-col md:flex-row flex-grow overflow-hidden">
    <!-- Sidebar -->
    <div class="md:w-1/5 bg-gray-800 p-4 overflow-y-auto h-full">
      <h2 class="text-xl font-bold mb-4 text-gray-100">Documents</h2>
      <ul>
        {#each documents as document}
          <li class="mb-2">
            <button
              type="button"
              class="w-full p-2 rounded-lg bg-gray-700 text-gray-200 shadow hover:bg-gray-600 transition"
              on:click={() => selectDocument(document.id)}
            >
              {document.title}
            </button>
          </li>
        {/each}
      </ul>
      {#if documents.length === 0}
        <p class="text-gray-400">Loading documents...</p>
      {/if}
    </div>

    <!-- Main content area -->
    <div class="md:w-4/5 bg-gray-900 p-4 md:p-8 flex flex-col h-full relative">
      {#if showLandingPage}
        <div class="flex flex-col flex-grow justify-center items-center">
          <h2 class="text-4xl font-bold text-center text-gray-100 mb-4 flex items-center">
            Welcome to UsPolicy.io!
            <span
              class="ml-3 px-2 py-1 bg-indigo-600 text-white text-sm font-semibold rounded-full animate-pulse"
            >
              Beta
            </span>
          </h2>
          <p class="text-lg text-center text-gray-300 mb-4">
            Select a document from the left to start asking questions.
            <br />
            All answers are solely from the selected document.
          </p>
        </div>
      {:else if selectedDocument}
        <!-- Dismissible Page Note on Top of Chat Box -->
        {#if showPageNote === true}
          <div
            class="absolute inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
            transition:fade={{ duration: 300 }}
            role="alert"
            aria-live="assertive"
          >
            <div
              class="bg-white text-gray-800 p-6 rounded-lg shadow-2xl flex flex-col items-start space-y-4"
              on:click|stopPropagation
            >
              <div>
                <p class="text-sm">
                  <strong>Note:</strong> Source page numbers are based on the PDF and not the document itself.
                </p>
                <label class="mt-4 flex items-center text-xs text-gray-600">
                  <input type="checkbox" bind:checked={dontShowAgain} />
                  <span class="ml-2">Don't show this again</span>
                </label>
              </div>
              <button
                type="button"
                on:click={dismissPageNote}
                class="self-end text-gray-600 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                aria-label="Dismiss notification"
              >
                <X size={20} />
              </button>
            </div>
          </div>
        {/if}

        <!-- Chat messages -->
        <div class="flex-1 overflow-y-auto mb-4" bind:this={chatContainer}>
          {#each messages as message}
            <div class={message.type === 'user' ? 'text-right' : 'text-left'}>
              <div
                class={`inline-block p-2 m-2 rounded-lg max-w-full md:max-w-xl ${
                  message.type === 'user'
                    ? 'bg-blue-700 text-white'
                    : 'bg-gray-700 text-gray-200 bot-message'
                }`}
                style="white-space: pre-wrap;"
              >
                {#if message.type === 'bot'}
                  {@html parseAssistantResponse(message.displayedText || message.text)}
                {:else}
                  {message.text}
                {/if}
              </div>
            </div>
          {/each}
        </div>

        <!-- Input form with original width -->
        <form on:submit={handleSubmit} class="flex flex-col md:flex-row w-full">
          <input
            type="text"
            bind:value={question}
            placeholder="Enter your question here..."
            class="flex-1 p-4 bg-gray-800 text-gray-200 border-2 border-gray-700 rounded-lg 
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent 
            transition-all duration-300 text-lg placeholder-gray-500 mb-2 md:mb-0"
          />
          <button
            type="submit"
            disabled={isLoading}
            class="md:ml-2 bg-indigo-600 text-white p-2 
            rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 
            focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if isLoading}
              <div class="spinner"></div>
            {:else}
              <Send size={24} />
            {/if}
          </button>
        </form>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Styles for hyperlinks in bot messages */
  :global(.bot-message a) {
    color: #1e90ff; /* DodgerBlue */
    text-decoration: underline;
  }

  :global(.bot-message a:hover) {
    color: #104e8b; /* Darker blue on hover */
  }

  /* Ensure bot messages have the correct text color */
  :global(.bot-message) {
    color: #e5e7eb; /* Tailwind's text-gray-200 */
  }

  .spinner {
    border: 4px solid rgba(255, 255, 255, 0.1);
    border-left-color: #6366f1; /* Indigo color */
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Responsive adjustments for the page note */
  @media (max-width: 640px) {
    .fixed.bottom-4.left-4.bg-white.text-gray-800.p-4.rounded-lg.shadow-2xl {
      width: 90%;
      left: 50%;
      transform: translateX(-50%);
    }
  }
</style>
