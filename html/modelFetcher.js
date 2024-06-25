// modelFetcher.js
export async function fetchAvailableModels(serverUrl, serverType) {
    const modelField = document.getElementById('modelField');
    modelField.innerHTML = '<option value="">Loading models...</option>';

    try {
        let models;

        if (serverType === 'ollama') {
            console.log('Fetching Ollama models from:', `${serverUrl}/api/tags`);
            const response = await fetch(`${serverUrl}/api/tags`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Received data:', data);
            models = data.models.map(model => model.name);
        } else if (serverType === 'llama.cpp') {
            console.log('Using fixed model list for llama.cpp');
            models = ['llama-2-7b', 'llama-2-13b', 'llama-2-70b'];
        } else {
            console.error(`Unsupported server type: ${serverType}`);
            throw new Error(`Unsupported server type: ${serverType}`);
        }

        console.log('Available models:', models); // Debug output

        // Clear existing options and add the placeholder
        modelField.innerHTML = '<option value="">--Please choose a model--</option>';

        // Add new model options to the dropdown
        models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelField.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching models:', error);
        modelField.innerHTML = `<option value="">Error: ${error.message}</option>`;
    }
}
