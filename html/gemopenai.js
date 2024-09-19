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
            const tfc = (firstCharTime - startTime).toFixed(2);
            const totalTime = (endTime - startTime) / 1000; // in seconds
            const cps = (result.length / totalTime).toFixed(2);

            const statsDiv = document.createElement('div');
            statsDiv.innerHTML = `<p>TFC: ${tfc} ms, CPS: ${cps} chars/sec</p>`;
            responseDiv.appendChild(statsDiv);
        }
        console.log(`Inference time: ${endTime - startTime} ms`);

        if (usage) {
            const usageStats = `\n\nTokens used: ${usage.total_tokens} (Prompt: ${usage.prompt_tokens}, Completion: ${usage.completion_tokens})`;
            assistantMessage.innerHTML += marked.parse(usageStats);
        }
    } catch (error) {
        console.error('Error in sendGemOpenAIRequest:', error);
        responseDiv.textContent = `Error: ${error.message}`;
    }
}