<script>
  import { onMount } from 'svelte';
  import { Send } from 'lucide-svelte';

  let documents = [];
  let selectedDocument = null;
  let question = '';
  let answer = '';
  let isLoading = false;
  let showLandingPage = true;
  let messages = [];

  onMount(async () => {
    await fetchDocuments();
  });

  async function fetchDocuments() {
    try {
      const response = await fetch('https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/documents', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
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
    selectedDocument = documents.find(doc => doc.id === id);
    question = '';
    answer = '';
    showLandingPage = false;
    messages = [];
    console.log('Selected document:', selectedDocument);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (question.trim()) {
      if (!selectedDocument) {
        console.error('No document selected.');
        return;
      }

      const userQuestion = question.trim(); // Store the question
      isLoading = true;
      answer = '';
      messages = [...messages, { type: 'user', text: userQuestion }];
      question = ''; // Clear the input box immediately
      console.log('Messages after user input:', messages);

      try {
        const response = await fetch('https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userQuestion,
            documentId: selectedDocument.id,
          }),
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
          throw new Error(`Failed to fetch answer: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Received data:', data);

        messages = [...messages, { type: 'bot', text: data.response }];
        console.log('Messages after bot response:', messages);
      } catch (error) {
        console.error('Error fetching answer:', error);
        messages = [...messages, { type: 'bot', text: 'Sorry, there was an error fetching the answer. Please try again.' }];
      } finally {
        isLoading = false;
      }
    }
  }
</script>

<div class="h-screen bg-gray-900 flex flex-col">
  <!-- Header -->
  <header class="bg-gray-800 text-gray-100 p-4 flex-shrink-0">
    <h1 class="text-3xl font-bold">UsPolicy.io</h1>
    {#if selectedDocument}
      <h2 class="text-xl mt-1">{selectedDocument.title}</h2>
    {/if}
  </header>

  <div class="flex flex-grow overflow-hidden">
    <!-- Smaller left-hand scrollable column with document list -->
    <div class="w-1/5 bg-gray-800 p-4 overflow-y-auto h-full">
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
    <div class="w-4/5 bg-gray-900 p-8 flex flex-col h-full">
      {#if showLandingPage}
        <div class="flex flex-col flex-grow justify-center items-center">
          <h2 class="text-4xl font-bold text-center text-gray-100 mb-4 flex items-center">
            Welcome to UsPolicy.io!
            <span class="ml-3 px-2 py-1 bg-indigo-600 text-white text-sm font-semibold rounded-full animate-pulse">
              Beta
            </span>
          </h2>
          <p class="text-lg text-center text-gray-300 mb-4">
            Select a document from the left to start asking questions.
            <br>
            All answers are solely from the selected document.
          </p>
        </div>
      {:else if selectedDocument}
        <!-- Chat messages -->
        <div class="flex-1 overflow-y-auto mb-4">
          {#each messages as message}
            <div class={message.type === 'user' ? 'text-right' : 'text-left'}>
              <div class={`inline-block p-2 m-2 rounded-lg max-w-xl ${message.type === 'user' ? 'bg-blue-700 text-white' : 'bg-gray-700 text-gray-200'}`}>
                {message.text}
              </div>
            </div>
          {/each}
        </div>

        <!-- Input form -->
        <form on:submit={handleSubmit} class="flex">
          <input
            type="text"
            bind:value={question}
            placeholder="Enter your question here..."
            class="flex-1 p-4 bg-gray-800 text-gray-200 border-2 border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 text-lg placeholder-gray-500"
          />
          <button type="submit" disabled={isLoading} class="ml-2 bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
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
