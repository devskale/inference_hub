// main.js
import { displayUserMessage, addSpinner, removeSpinner, displayAssistantMessage, handleError } from './utils.js';
import { sendOllamaRequest } from './ollama.js';
import { sendLlamaRequest } from './llamacpp.js';

let controller;

document.getElementById('chatForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const inputField = document.getElementById('inputField').value;
    const responseDiv = document.getElementById('response');
    const stopButton = document.getElementById('stopButton');
    const optionField = document.getElementById('optionField');
    const selectedURL = optionField.options[optionField.selectedIndex].value;
    const apiType = optionField.options[optionField.selectedIndex].text.toLowerCase();

    displayUserMessage(responseDiv, inputField);

    const spinner = addSpinner(responseDiv);

    controller = new AbortController();
    const signal = controller.signal;

    stopButton.style.display = 'inline-block';

    const startTime = performance.now();

    try {
        if (apiType.includes('ollama')) {
            // add a model for the ollama api
            if (apiType.includes('llama3')) {
                var model = 'llama3';
            } else {
                var model = 'phi3';
            }
            await sendOllamaRequest(selectedURL, model, inputField, responseDiv, signal, startTime);
        } else if (apiType.includes('llama')) {
            await sendLlamaRequest(selectedURL, inputField, responseDiv, signal, startTime);
        }
    } catch (error) {
        handleError(responseDiv, error);
    } finally {
        stopButton.style.display = 'none';
        removeSpinner(responseDiv, spinner);
    }

    document.getElementById('inputField').value = '';
});

document.getElementById('stopButton').addEventListener('click', function () {
    if (controller) {
        controller.abort();
    }
});
