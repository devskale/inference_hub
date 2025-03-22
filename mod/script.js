document.getElementById('fetchData').addEventListener('click', async () => {
    const responseElement = document.getElementById('response');
    
    YOUR_API_KEY = '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';  // Replace with your OpenAI API key


    try {
        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${YOUR_API_KEY}`,  // Replace with your OpenAI API key
            },
            body: JSON.stringify({
                model: 'meta-llama/llama-3-8b-instruct:free',
                messages: [{ role: 'user', content: 'Say this is a test' }],
            }),
        });
        
        const data = await response.json();
        responseElement.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        console.error('Error fetching data:', error);
        responseElement.textContent = 'Error fetching data';
    }
});
