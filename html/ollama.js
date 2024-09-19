// ollama.js

import { displayAssistantMessage } from './utils.js';

// Configure marked to use highlight.js for code syntax highlighting
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

// Configure marked to use highlight.js for code syntax highlighting
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

export async function sendOllamaRequest(url, model, input, responseDiv, signal, startTime) {
    const data = {
        model: model,
        messages: [
            { role: 'system', content: 'You are a helpful AI agent.' },
            { role: 'user', content: input }
        ]
    };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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

        let firstCharTime = null;
        const firstChunk = await reader.read();
        if (!firstChunk.done) {
            firstCharTime = performance.now();
            const textChunk = decoder.decode(firstChunk.value);
            const lines = textChunk.split('\n');
            for (const line of lines) {
                if (line.trim() === '') continue;
                try {
                    const json = JSON.parse(line);
                    if (json.done === false) {
                        result += json.message.content;
                        assistantMessage.innerHTML = marked.parse(result);
                        responseDiv.scrollTop = responseDiv.scrollHeight;
                    }
                } catch (error) {
                    console.error('JSON parse error:', error);
                }
            }
        }

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const textChunk = decoder.decode(value);

            const lines = textChunk.split('\n');
            for (const line of lines) {
                if (line.trim() === '') continue;
                try {
                    const json = JSON.parse(line);
                    if (json.done === false) {
                        result += json.message.content;
                        assistantMessage.innerHTML = marked.parse(result);
                        responseDiv.scrollTop = responseDiv.scrollHeight;
                    }
                } catch (error) {
                    console.error('JSON parse error:', error);
                }
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
            statsElement.innerHTML = `1st: ${tfc} s, tot ${totalTime.toFixed(1)} s<br>${cps} char/s,`;
            statsDiv.appendChild(statsElement);

            responseDiv.appendChild(statsDiv);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Fetch error:', error);
            throw error;
        }
    }
}