// gemopenai.js

import { displayAssistantMessage } from './utils.js';
import { GEMINI_TOKEN } from './config.js'; // Import the bearer token from config

export async function sendGemOpenAIRequest(url, model, input, responseDiv, signal, startTime) {
    const data = {
        "model": model, // Specify the model you want to use
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
                'Authorization': `Bearer ${GEMINI_TOKEN}` // Include the Bearer token
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
                        assistantMessage.textContent += delta.content;
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
        console.log(`Inference time: ${endTime - startTime} ms`);

        if (usage) {
            const usageStats = `\n\nTokens used: ${usage.total_tokens} (Prompt: ${usage.prompt_tokens}, Completion: ${usage.completion_tokens})`;
            assistantMessage.textContent += usageStats;
        }
    } catch (error) {
        console.error('Error in sendGemOpenAIRequest:', error);
        responseDiv.textContent = `Error: ${error.message}`;
    }
}