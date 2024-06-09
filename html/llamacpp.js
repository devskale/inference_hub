// llamacpp.js

import { displayAssistantMessage } from './utils.js';

export async function sendLlamaRequest(url, input, responseDiv, signal) {
    const data = {
        "messages": [
            { "role": "system", "content": "You are a helpful assistant." },
            { "role": "user", "content": input }
        ],
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": true
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
            const chunk = decoder.decode(value, { stream: true });

            const lines = chunk.split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonChunk = line.substring(6).trim();
                    try {
                        const parsedChunk = JSON.parse(jsonChunk);
                        if (parsedChunk.choices && parsedChunk.choices.length > 0) {
                            const content = parsedChunk.choices[0].delta.content;
                            if (content) {
                                result += content;
                                assistantMessage.innerText = result;
                            }
                        }
                    } catch (jsonError) {
                        console.error("Error parsing chunk as JSON: ", jsonError);
                    }
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
