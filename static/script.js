document.addEventListener('DOMContentLoaded', () => {
    const smilesInput = document.getElementById('smilesInput');
    const predictBtn = document.getElementById('predictBtn');
    const resultCard = document.querySelector('.result-card');
    const predictionValue = document.getElementById('predictionValue');
    const predictionStatus = document.getElementById('predictionStatus');

    // Show result card initially but empty
    resultCard.classList.add('visible');

    predictBtn.addEventListener('click', async () => {
        const smiles = smilesInput.value.trim();

        if (!smiles) {
            alert('Please enter a valid SMILES string.');
            return;
        }

        // UI State: Loading
        predictBtn.disabled = true;
        predictBtn.textContent = 'Analyzing...';
        predictionValue.style.opacity = '0.5';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ smiles: smiles })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Prediction failed');
            }

            const data = await response.json();

            // UI State: Success
            predictionValue.textContent = data.pIC50.toFixed(2);
            predictionStatus.textContent = 'Prediction Successful';
            predictionValue.style.color = '#4ade80'; // Success green

            // Reset other cards
            const chemblCard = document.getElementById('chemblCard');
            const dockingCard = document.getElementById('dockingCard');

            chemblCard.classList.remove('hidden');
            chemblCard.classList.add('visible');

            dockingCard.classList.remove('hidden');
            dockingCard.classList.add('visible');

            // Fetch ChEMBL Details
            fetchChemblDetails(smiles);

            // Reset Docking Area
            document.getElementById('downloadArea').classList.add('hidden');

        } catch (error) {
            console.error('Error:', error);
            predictionValue.textContent = 'Error';
            predictionStatus.textContent = error.message;
            predictionValue.style.color = '#f87171'; // Error red
        } finally {
            // UI State: Reset
            predictBtn.disabled = false;
            predictBtn.textContent = 'Predict';
            predictionValue.style.opacity = '1';
        }
    });

    // Allow Enter key to submit
    smilesInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            predictBtn.click();
        }
    });

    // Docking 3D Generation
    const generate3dBtn = document.getElementById('generate3dBtn');
    generate3dBtn.addEventListener('click', async () => {
        const smiles = smilesInput.value.trim();
        generate3dBtn.disabled = true;
        generate3dBtn.textContent = 'Generating...';

        try {
            const response = await fetch('/generate_3d', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles: smiles })
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail);

            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = data.file_url;
            downloadLink.download = data.filename;

            document.getElementById('downloadArea').classList.remove('hidden');

        } catch (e) {
            alert('Error generating 3D structure: ' + e.message);
        } finally {
            generate3dBtn.disabled = false;
            generate3dBtn.textContent = 'Generate 3D Structure';
        }
    });

    async function fetchChemblDetails(smiles) {
        const container = document.getElementById('chemblData');
        container.innerHTML = '<p>Searching ChEMBL database...</p>';

        try {
            const response = await fetch('/chembl_details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ smiles: smiles })
            });

            const data = await response.json();

            if (data.found) {
                container.innerHTML = `
                    <div><strong>Name:</strong> ${data.name}</div>
                    <div><strong>ChEMBL ID:</strong> <a href="https://www.ebi.ac.uk/chembl/compound_report_card/${data.chembl_id}" target="_blank" style="color:#60a5fa">${data.chembl_id}</a></div>
                    <div><strong>Max Phase:</strong> ${data.phase || 'N/A'}</div>
                    <div><strong>Mol Weight:</strong> ${data.mw || 'N/A'}</div>
                    <div><strong>LogP:</strong> ${data.logp || 'N/A'}</div>
                `;
            } else {
                container.innerHTML = '<p>No exact match found in ChEMBL.</p>';
            }
        } catch (e) {
            container.innerHTML = '<p>Error fetching details.</p>';
        }
    }
});
