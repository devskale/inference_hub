import { displayAssistantMessage } from './utils.js';
import { GEMINI_TOKEN } from './config.js';

// Configure marked to use highlight.js for code syntax highlighting
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

export async function sendGemOpenAIRequest(url, model, input, responseDiv, signal, startTime) {
    const data = {
        "model": model,
        "messages": [{"role": "user", "content": input}],
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": true
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${GEMINI_TOKEN}`
            },
            body: JSON.stringify(data),
            signal: signal
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = displayAssistantMessage(responseDiv, '', true);
        let result = '';
        let usage = null;

        let firstCharTime = null;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n').filter(line => line.trim() !== '');
            for (const line of lines) {
                if (line === 'data: [DONE]') {
                    break;
                }
                if (line.startsWith('data: ')) {
                    const json = JSON.parse(line.substring(6));
                    const delta = json.choices[0].delta;
                    if (delta && delta.content) {
                        result += delta.content;
                        // Convert markdown to HTML and update the display
                        assistantMessage.innerHTML = marked.parse(result);
                    }
                    if (json.usage) {
                        usage = json.usage;
                    }
                }
            }

            if (!firstCharTime) {
                firstCharTime = performance.now();
            }
        }

        const endTime = performance.now();

        if (firstCharTime) {
            const tfc = ((firstCharTime - startTime) / 1000).toFixed(1); // in seconds
            const totalTime = (endTime - startTime) / 1000; // in seconds
            const cps = (result.length / totalTime).toFixed(1);

            const statsDiv = document.createElement('div');
            const statsElement = document.createElement('p');

            statsElement.className = 'status-light';
            //statsElement.textContent = `1st: ${tfc} s, ${cps} ch/s,<br>T ${totalTime.toFixed(1)} s`;
            statsElement.innerHTML = `1st: ${tfc} s, tot ${totalTime.toFixed(1)} s, ${cps} char/s,`;
            if (usage) {
                const usageStats = `<br>Tokens used: ${usage.total_tokens} (Prompt: ${usage.prompt_tokens}, Completion: ${usage.completion_tokens})`;
                statsElement.innerHTML += usageStats;
            }
                statsDiv.appendChild(statsElement);

            responseDiv.appendChild(statsDiv);
        }
        console.log(`Inference time: ${endTime - startTime} ms`);



    } catch (error) {
        console.error('Error in sendGemOpenAIRequest:', error);
        responseDiv.textContent = `Error: ${error.message}`;
    }
}