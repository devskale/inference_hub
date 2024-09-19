export async function fetchAvailableModels(serverUrl, serverType) {
    const modelField = document.getElementById('modelField');
    modelField.innerHTML = '<option value="">Loading models...</option>';

    try {
        let models;

        if (serverType === 'ollama') {
            const fetchUrl = `${serverUrl}/api/tags`;
            console.log('Fetching Ollama models from:', fetchUrl);

            // Ensure using HTTP
            const response = await fetch(fetchUrl, {
                method: 'GET',
                mode: 'cors',
                cache: 'no-cache',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                },
                redirect: 'follow',
                referrerPolicy: 'no-referrer',
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received data:', data);
            models = data.models.map(model => model.name);
        } else if (serverType === 'llama.cpp') {
            console.log('Using fixed model list for llama.cpp');
            models = ['llama-2-7b', 'llama-2-13b', 'llama-2-70b'];
        } else if (serverType === 'openai') {
            console.log('Using fixed model list for openai');
            models = ['llama-2-7b', 'llama-2-13b', 'llama-2-70b'];
        } else if (serverType === 'gemopenai') {
            console.log('Using fixed model list for gemopenai');
            models = ['gemini-1.5-pro-latest', 'gemini-1.5-flash-latest', 'gemini-1.5-pro-latest'];
        } else {
            console.error(`Unsupported server type: ${serverType}`);
            throw new Error(`Unsupported server type: ${serverType}`);
        }

        console.log('Available models:', models);

        modelField.innerHTML = '<option value="">--Please choose a model--</option>';
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

document.getElementById('serverField').addEventListener('change', async function() {
    const serverField = document.getElementById('serverField');
    const selectedOption = serverField.options[serverField.selectedIndex];
    const serverUrl = selectedOption.value;
    const serverType = selectedOption.getAttribute('data-description');

    await fetchAvailableModels(serverUrl, serverType);
});
