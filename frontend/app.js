const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const cameraInput = document.getElementById('camera-input');
const fileInfo = document.getElementById('file-info');
const convertBtn = document.getElementById('convert-btn');
const loadingBox = document.getElementById('loading-box');
const resultBox = document.getElementById('result-box');
const downloadLink = document.getElementById('download-link');
const targetFormatSelect = document.getElementById('target-format');
const templateStyleSelect = document.getElementById('template-style');
const actionCard = document.getElementById('action-card');

let selectedFile = null;
function updateTheme() {
    const format = targetFormatSelect.value;
    actionCard.classList.remove(
        'bg-red-950/20', 'border-red-500/50', 
        'bg-blue-950/20', 'border-blue-500/50', 
        'bg-emerald-950/20', 'border-emerald-500/50', 
        'bg-orange-950/20', 'border-orange-500/50'
    );
    dropZone.classList.remove(
        'border-red-500/40', 'bg-red-950/10',
        'border-blue-500/40', 'bg-blue-950/10',
        'border-emerald-500/40', 'bg-emerald-950/10',
        'border-orange-500/40', 'bg-orange-950/10'
    );
    convertBtn.classList.remove('bg-red-600', 'hover:bg-red-500', 'bg-blue-600', 'hover:bg-blue-500', 'bg-emerald-600', 'hover:bg-emerald-500', 'bg-orange-600', 'hover:bg-orange-500');
    if (format === '.pdf') {
        actionCard.classList.add('bg-red-950/20', 'border-red-500/50');
        dropZone.classList.add('border-red-500/40', 'bg-red-950/10');
        convertBtn.classList.add('bg-red-600', 'hover:bg-red-500');
    } else if (format === '.docx') {
        actionCard.classList.add('bg-blue-950/20', 'border-blue-500/50');
        dropZone.classList.add('border-blue-500/40', 'bg-blue-950/10');
        convertBtn.classList.add('bg-blue-600', 'hover:bg-blue-500');
    } else if (format === '.xlsx') {
        actionCard.classList.add('bg-emerald-950/20', 'border-emerald-500/50');
        dropZone.classList.add('border-emerald-500/40', 'bg-emerald-950/10');
        convertBtn.classList.add('bg-emerald-600', 'hover:bg-emerald-500');
    } else if (format === '.pptx') {
        actionCard.classList.add('bg-orange-950/20', 'border-orange-500/50');
        dropZone.classList.add('border-orange-500/40', 'bg-orange-950/10');
        convertBtn.classList.add('bg-orange-600', 'hover:bg-orange-500');
    }
}

targetFormatSelect.addEventListener('change', updateTheme);
updateTheme();
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('scale-[1.01]');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('scale-[1.01]');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('scale-[1.01]');
    if (e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

cameraInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
        targetFormatSelect.value = '.pdf';
        updateTheme();
    }
});

function handleFileSelection(file) {
    selectedFile = file;
    fileInfo.textContent = `File terpilih: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    fileInfo.classList.remove('hidden');
    convertBtn.removeAttribute('disabled');
    resultBox.classList.add('hidden');
}
convertBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const targetFormat = targetFormatSelect.value;
    const templateStyle = templateStyleSelect.value;

    convertBtn.setAttribute('disabled', 'true');
    loadingBox.classList.remove('hidden');
    resultBox.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('target_format', targetFormat);
    formData.append('template_style', templateStyle);

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || 'Terjadi kesalahan pada server.');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        downloadLink.href = url;
        downloadLink.download = `converted_${selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.')) || selectedFile.name}${targetFormat}`;
        
        loadingBox.classList.add('hidden');
        resultBox.classList.remove('hidden');
    } catch (error) {
        alert(`Gagal Konversi: ${error.message}`);
        loadingBox.classList.add('hidden');
    } finally {
        convertBtn.removeAttribute('disabled');
    }
});