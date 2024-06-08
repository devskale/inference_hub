let controller;

document.getElementById('chatForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const inputField = document.getElementById('inputField').value;
    const responseDiv = document.getElementById('response');
    const stopButton = document.getElementById('stopButton');

    // Display user's message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user';
    userMessage.textContent = inputField;
    responseDiv.appendChild(userMessage);

    // Scroll to the bottom of the response div
    responseDiv.scrollTop = responseDiv.scrollHeight;

    const data = {
        model: 'phi3',
        messages: [
            { role: 'system', content: 'You are a helpful AI agent.' },
            { role: 'user', content: inputField }
        ]
    };

    controller = new AbortController();
    const signal = controller.signal;

    // Show the stop button
    stopButton.style.display = 'inline-block';

    try {
        const response = await fetch('http://localhost:11434/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            signal: signal
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = document.createElement('div');
        assistantMessage.className = 'message assistant';
        responseDiv.appendChild(assistantMessage);
        let result = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                break;
            }
            const textChunk = decoder.decode(value);

            // Split the response into individual JSON objects
            const lines = textChunk.split('\n');
            for (const line of lines) {
                if (line.trim() === '') continue;
                try {
                    const json = JSON.parse(line);
                    if (json.done === false) {
                        result += json.message.content;
                        assistantMessage.textContent = result;

                        // Scroll to the bottom of the response div
                        responseDiv.scrollTop = responseDiv.scrollHeight;
                    }
                } catch (error) {
                    console.error('JSON parse error:', error);
                }
            }
        }
    } catch (error) {
        console.error('Error:', error);
        if (error.name === 'AbortError') {
            assistantMessage.textContent += '..';
        }
    } finally {
        // Hide the stop button when streaming is done
        stopButton.style.display = 'none';
    }

    document.getElementById('inputField').value = ''; // Clear the input field
});

document.getElementById('stopButton').addEventListener('click', function () {
    if (controller) {
        controller.abort(); // Abort the fetch request
    }
});
