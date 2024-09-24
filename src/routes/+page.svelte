<script>
  import { onMount } from 'svelte';
  import { Send } from 'lucide-svelte';
  import { marked } from 'marked';

  let documents = [];
  let selectedDocument = null;
  let question = '';
  let answer = '';
  let isLoading = false;
  let showLandingPage = true;
  let messages = [];
  let chatContainer;

  onMount(async () => {
    await fetchDocuments();
  });

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
        throw new Error(
          `Failed to fetch documents: ${response.status} ${response.statusText}`
        );
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
    answer = '';
    showLandingPage = false;
    messages = [];
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
      answer = '';
      messages = [...messages, { type: 'user', text: userQuestion }];
      question = '';

      // Check if response is cached in LocalStorage
      const cachedData = localStorage.getItem(userQuestion);
      if (cachedData) {
        const { response, timestamp } = JSON.parse(cachedData);
        const cacheDuration = 3600 * 1000; // 1 hour in milliseconds
        if (Date.now() - timestamp < cacheDuration) {
          messages = [...messages, { type: 'bot', text: response }];
          console.log('Retrieved response from cache:', response);
          isLoading = false;
          return;
        } else {
          // Cache expired
          localStorage.removeItem(userQuestion);
          console.log('Cache expired for question:', userQuestion);
        }
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
              documentId: selectedDocument.id
            })
          }
        );

        // Clone the response to read it without consuming the original
        const responseClone = response.clone();
        const responseText = await responseClone.text();

        let data;
        try {
          data = JSON.parse(responseText);
        } catch (jsonError) {
          throw new Error('Invalid JSON response from the API');
        }

        // Check if the response indicates inability to answer
        const isUnableToAnswer = data.response.trim().toLowerCase().includes('unable to answer your query from the text');

        // Prepare the assistant's message
        const assistantMessage = {
          type: 'bot',
          text: data.response,
          displayedText: '',
          typing: true
        };

        // If able to answer, append source pages if available
        if (!isUnableToAnswer) {
          if (data.sourcePages && Array.isArray(data.sourcePages) && data.sourcePages.length > 0) {
            const sourcesText = data.sourcePages.map(page => `Source: [Page ${page}](/path-to-document?page=${page})`).join('\n');
            assistantMessage.text += `\n\n${sourcesText}`;
          }

          // Cache the response in LocalStorage
          const cacheEntry = {
            response: data.response,
            timestamp: Date.now()
          };
          localStorage.setItem(userQuestion, JSON.stringify(cacheEntry));
          console.log('Cached response:', cacheEntry);
        } else {
          console.log('Assistant unable to answer the query.');
        }

        // Add the assistant's message to messages
        messages = [...messages, assistantMessage];

        // Start the typing effect
        typeAssistantMessage(assistantMessage);
      } catch (error) {
        console.error('Error fetching answer:', error);
        messages = [
          ...messages,
          {
            type: 'bot',
            text: 'Sorry, there was an error fetching the answer. Please try again.',
            displayedText: '',
            typing: false
          }
        ];
      } finally {
        isLoading = false;
      }
    }
  }

  function parseAssistantResponse(text) {
    // Check if the assistant is unable to answer the query
    const unableToAnswer = text.trim().toLowerCase().includes('unable to answer your query from the text');
    if (unableToAnswer) {
      // Return the response without adding any source pages
      return `<p>${sanitizeHTML(text.trim())}</p>`;
    }

    // Only proceed to split and process source pages if the assistant is able to answer
    let content = text;
    let pagesLine = '';

    if (text.includes('Source page numbers:')) {
      // Split the response into main content and source pages
      [content, pagesLine] = text.split('Source page numbers:');
    }

    // Parse the main content from Markdown to HTML
    let parsedContent = marked.parse(content.trim());

    // Process source pages if they exist
    if (pagesLine && selectedDocument && isValidUrl(selectedDocument.source_url)) {
      // Extract and clean page numbers from the pagesLine
      const pagesText = pagesLine.trim().replace(/[\[\]]/g, '');
      const pageNumbers = pagesText.split(',').map((num) => num.trim()).filter(Boolean);
      if (unableToAnswer) {
        // Split the response into main content and source pages
        pagesLine = '';
      }
      // Construct hyperlinks for each page number
      if (pageNumbers.length > 0) {
        const pageLinks = pageNumbers.map((page) => {
          const source_url = `${selectedDocument.source_url}#page=${page}`;
          return `<a href="${sanitizeURL(source_url)}" target="_blank" rel="noopener noreferrer">Page ${page}</a>`;
        });

        // Append the hyperlinks to the parsed content
        const pagesHtml = `<p>Source pages: ${pageLinks.join(', ')}</p>`;
        parsedContent += pagesHtml;
      }
    }

    return parsedContent;
}


  // Helper function to validate URL
  function isValidUrl(string) {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  }

  // Function to sanitize HTML (using DOMPurify or similar library is recommended)
  function sanitizeHTML(html) {
    // Simple sanitization example (replace with a robust solution like DOMPurify)
    const tempDiv = document.createElement('div');
    tempDiv.textContent = html;
    return tempDiv.innerHTML;
  }

  // Function to sanitize URLs
  function sanitizeURL(url) {
    try {
      const sanitizedUrl = new URL(url);
      return sanitizedUrl.href;
    } catch (_) {
      console.error('Invalid URL:', url);
      return '#';
    }
  }

  // Typing effect for assistant's message
  function typeAssistantMessage(message) {
    const fullText = message.text;
    let index = 0;
    const typingSpeed = 10; // Adjust typing speed here (milliseconds per character)

    function typeCharacter() {
      if (index < fullText.length) {
        // Append the next character
        message.displayedText += fullText.charAt(index);
        index++;

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

  // Function to scroll to the bottom of the chat container
  function scrollToBottom() {
    setTimeout(() => {
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 0);
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
    <div class="md:w-4/5 bg-gray-900 p-4 md:p-8 flex flex-col h-full">
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

        <!-- Input form -->
        <form on:submit={handleSubmit} class="flex flex-col md:flex-row">
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
</style>
