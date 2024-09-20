<script>
  import { Send, ArrowRight } from 'lucide-svelte';
  let question = '';
  let answer = '';
  let isLoading = false;

  async function handleSubmit(event) {
    event.preventDefault();
    if (question.trim()) {
      isLoading = true;
      answer = '';

      try {
        // Replace with your actual API endpoint
        const response = await fetch('https://vp1zl5sk39.execute-api.us-east-1.amazonaws.com/default/uspolicy/', {
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
        console.log(data); // Debug: Log the entire response
        // Set the answer from `data.response`
        answer = data.response;
      } catch (error) {
        console.error('Error fetching answer:', error);
        answer = 'Sorry, there was an error fetching the answer. Please try again.';
      } finally {
        isLoading = false;
      }
    }
  }
</script>

<div class="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-100 flex items-center justify-center p-4">
  <div class="w-full max-w-3xl bg-white rounded-2xl shadow-2xl p-8 space-y-8 transition-all duration-500 ease-in-out">
    <h1 class="text-4xl font-bold text-center text-gray-800 mb-8">
      Ask a Question About Project 2025
      <span class="block text-lg font-normal text-gray-500 mt-2">Protect American Democracy</span>
    </h1>

    <form on:submit={handleSubmit} class="space-y-4">
      <div class="relative">
        <input
            type="text"
            bind:value={question}
            placeholder="Enter your question here..."
            class="w-full p-4 pr-12 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-300 text-lg"
        />
        <button type="submit" disabled={isLoading} class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-indigo-500 text-white p-2 rounded-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-700 focus:ring-offset-2 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
          {#if isLoading}
            <div class="spinner"></div>
          {:else}
            <Send size={24} />
          {/if}
        </button>
      </div>
    </form>

    {#if isLoading}
      <div class="space-y-3 animate-pulse">
        <div class="h-4 bg-gray-200 rounded"></div>
        <div class="h-4 bg-gray-200 rounded w-5/6"></div>
        <div class="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    {/if}

    {#if answer && !isLoading}
      <div class="bg-gradient-to-r from-indigo-50 to-cyan-50 p-6 rounded-lg shadow-inner transition-all duration-500 ease-in-out animate-fadeIn">
        <h2 class="text-xl font-semibold mb-4 flex items-center text-indigo-700">
          <ArrowRight class="mr-2" size={24} />
          Answer
        </h2>
        <p class="text-gray-700 leading-relaxed text-lg">{answer}</p>
      </div>
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
