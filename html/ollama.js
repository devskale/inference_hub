// ollama.js

import { displayAssistantMessage } from './utils.js';

export async function sendOllamaRequest(url, input, responseDiv, signal) {
    const data = {
        model: 'phi3',
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
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Fetch error:', error);
            throw error;
        }
    }
}
