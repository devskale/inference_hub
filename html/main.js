// main.js
import { displayUserMessage, addSpinner, removeSpinner, displayAssistantMessage, handleError } from './utils.js';
import { sendOllamaRequest } from './ollama.js';
import { sendLlamaRequest } from './llamacpp.js';
import { sendGemOpenAIRequest } from './gemopenai.js';
import { fetchAvailableModels } from './modelFetcher.js';
import { servers } from './config.js';

let controller;

// Populate server field with options from config
const serverField = document.getElementById('serverField');
servers.forEach(server => {
    const option = document.createElement('option');
    option.value = server.url;
    option.textContent = server.url;
    option.setAttribute('data-description', server.description);
    serverField.appendChild(option);
});

// Set default server and fetch models
const defaultServer = serverField.getAttribute('data-default');
if (defaultServer) {
    serverField.value = defaultServer;
    const selectedOption = serverField.options[serverField.selectedIndex];
    const serverType = selectedOption.getAttribute('data-description');
    fetchAvailableModels(defaultServer, serverType).then(() => {
        // Set default model after models are fetched
        const modelField = document.getElementById('modelField');
        const defaultModel = modelField.getAttribute('data-default');
        if (defaultModel) {
            modelField.value = defaultModel;
        }
    });
}

// Event listener for server field change
serverField.addEventListener('change', async function() {
    const selectedOption = this.options[this.selectedIndex];
    const serverUrl = selectedOption.value;
    const description = selectedOption.getAttribute('data-description');
    const modelField = document.getElementById('modelField');
    let serverType = '';

    // Determine the server type based on the description
    if (description.includes('ollama')) {
        serverType = 'ollama';
    } else if (description.includes('llama.cpp')) {
        serverType = 'llama.cpp';
    } else if (description.includes('gemopenai')) {
        serverType = 'gemopenai';
    } else if (description.includes('openai')) {
        serverType = 'openai';
    } else {
        serverType = ''; // Or set a default/fallback server type
    }

    if (serverUrl && serverType) {
        try {
            // Show loading message while fetching models
            modelField.innerHTML = '<option value="">Loading models...</option>';
            
            // Fetch available models for the selected server and server type
            await fetchAvailableModels(serverUrl, serverType);
        } catch (error) {
            console.error('Error in fetchAvailableModels:', error);
            // Display error message if fetching models fails
            modelField.innerHTML = `<option value="">Error: ${error.message}</option>`;
        }
    } else {
        // Prompt the user to select a server first
        modelField.innerHTML = '<option value="">--Please choose a server first--</option>';
    }
});

document.getElementById('chatForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const inputField = document.getElementById('inputField').value;
    const responseDiv = document.getElementById('response');
    const stopButton = document.getElementById('stopButton');
    const serverField = document.getElementById('serverField');
    const modelField = document.getElementById('modelField');

    const selectedServer = serverField.value;
    const selectedModel = modelField.value;

    if (!selectedServer || !selectedModel) {
        alert('Please select both a server and a model.');
        return;
    }

    displayUserMessage(responseDiv, inputField);
    const spinner = addSpinner(responseDiv);
    controller = new AbortController();
    const signal = controller.signal;
    stopButton.style.display = 'inline-block';
    const startTime = performance.now();

    try {
        const selectedOption = serverField.options[serverField.selectedIndex];
        const description = selectedOption.getAttribute('data-description');
        
        if (description.includes('ollama')) {
            await sendOllamaRequest(`${selectedServer}/api/chat`, selectedModel, inputField, responseDiv, signal, startTime);
        } else if (description.includes('llama.cpp')) {
            await sendLlamaRequest(`${selectedServer}/chat/completions`, inputField, responseDiv, signal, startTime);
        } else if (description.includes('openai')) {
            await sendGemOpenAIRequest(`${selectedServer}/v1/chat/completions`, selectedModel, inputField, responseDiv, signal, startTime);
        } else {
            throw new Error('Unsupported server type');
        }
    } catch (error) {
        handleError(responseDiv, error);
    } finally {
        stopButton.style.display = 'none';
        removeSpinner(responseDiv, spinner);
    }
    document.getElementById('inputField').value = '';
});

document.getElementById('stopButton').addEventListener('click', function() {
    if (controller) {
        controller.abort();
    }
});

// Toggle sidebar on mobile
document.getElementById('settingsToggle').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('show');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const settingsToggle = document.getElementById('settingsToggle');
    if (!sidebar.contains(event.target) && event.target !== settingsToggle) {
        sidebar.classList.remove('show');
    }
});