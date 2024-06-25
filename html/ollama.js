// ollama.js

import { displayAssistantMessage } from './utils.js';

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
                        assistantMessage.innerText = result;
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
                        assistantMessage.innerText = result;
                        responseDiv.scrollTop = responseDiv.scrollHeight;
                    }
                } catch (error) {
                    console.error('JSON parse error:', error);
                }
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
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Fetch error:', error);
            throw error;
        }
    }
}
