<script>
  import { onMount } from 'svelte';
  import { Send } from 'lucide-svelte';

  let documents = [];
  let selectedDocument = null;
  let question = '';
  let answer = '';
  let isLoading = false;
  let showLandingPage = true; // Track whether to show the landing page
  let messages = []; // Store chat messages

  onMount(async () => {
    await fetchDocuments();
  });

  async function fetchDocuments() {
    try {
      const response = await fetch('https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/documents');
      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }
      documents = await response.json();
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  }

  function selectDocument(id) {
    selectedDocument = documents.find(doc => doc.id === id);
    question = ''; // Clear the question when a new document is selected
    answer = '';   // Clear the previous answer
    showLandingPage = false; // Hide landing page after document selection
    messages = []; // Clear previous messages
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (question.trim()) {
      isLoading = true;
      answer = '';
      messages.push({ type: 'user', text: question }); // Add user question to messages

      try {
        const response = await fetch('https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: question }),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch answer');
        }

        const data = await response.json();
        messages.push({ type: 'bot', text: data.response }); // Add bot answer to messages
      } catch (error) {
        console.error('Error fetching answer:', error);
        messages.push({ type: 'bot', text: 'Sorry, there was an error fetching the answer. Please try again.' });
      } finally {
        isLoading = false;
        question = ''; // Clear the input after sending
      }
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-100 flex flex-col">
  <!-- Smaller left-hand scrollable column with document list -->
  <div class="w-1/5 bg-gray-100 p-4 overflow-y-auto h-screen">
    <h2 class="text-xl font-bold mb-4">Documents</h2>
    <ul>
      {#each documents as document}
        <li class="mb-2">
          <button
            type="button"
            class="w-full p-2 rounded-lg bg-white shadow hover:bg-indigo-200 transition"
            on:click={() => selectDocument(document.id)}
          >
            {document.title}
          </button>
        </li>
      {/each}
    </ul>
    {#if documents.length === 0}
      <p class="text-gray-600">Loading documents...</p>
    {/if}
  </div>

  <!-- Main content area -->
  <div class="w-4/5 max-w-2xl bg-white rounded-2xl shadow-2xl p-8 flex flex-col flex-1">
    {#if showLandingPage}
      <div class="flex flex-col flex-grow justify-center items-center">
        <h1 class="text-4xl font-bold text-center text-gray-800 mb-4">
          Welcome to the Document Chat Interface
        </h1>
        <p class="text-lg text-center mb-4">
          Select a document from the left to start asking questions.
        </p>
      </div>
    {:else if selectedDocument}
      <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">
        {selectedDocument.title}
      </h1>

      <div class="flex-1 overflow-y-auto mb-4">
        {#each messages as message}
          <div class={message.type === 'user' ? 'text-right' : 'text-left'}>
            <div class={`p-2 rounded-lg ${message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'}`}>
              {message.text}
            </div>
          </div>
        {/each}
      </div>

      <form on:submit={handleSubmit} class="flex">
        <input
          type="text"
          bind:value={question}
          placeholder="Enter your question here..."
          class="flex-1 p-4 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 text-lg"
        />
        <button type="submit" disabled={isLoading} class="ml-2 bg-indigo-500 text-white p-2 rounded-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-700 focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
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

<style>
  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
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
