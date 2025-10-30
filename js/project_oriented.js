/**
 * =====================================================================================
 * Aurora IDE - Project Oriented Configuration System (Enhanced with File Mode)
 * =====================================================================================
 */

class ProjectOrientedManager {
  constructor() {
    // Core configuration
    this.CONFIG_FILENAME = 'projectOriented.json';
    this.FILE_MODE_CONFIG_FILENAME = 'fileOriented.json';
    this.ICON_TRANSITION_DURATION = 300;
    
    // File Mode state
    this.isFileMode = false;
    
    // State management
    this.currentConfig = {
      topLevelFile: '',
      testbenchFile: '',
      gtkwaveFile: '',
      processors: [],
      iverilogFlags: '',
      simuDelay: '200000',
      showArraysInGtkwave: 0
    };
    
    // File mode configuration
    this.fileModeConfig = {
      topLevelFile: '',
      synthesizableFiles: []
    };
    
    // File storage
    this.synthesizableFiles = [];
    this.testbenchFiles = [];
    this.gtkwFiles = [];
    
    // Processor management
    this.availableProcessors = [];
    this.selectedProcessors = new Set();
    this.processorInstancesMap = {};
    
    // DOM element cache
    this.elements = {};
    
    // Initialize
    this.init();
  }
  
  async init() {
    try {
      this.cacheElements();
      this.setupEventListeners();
      this.enhanceDropZones();
      await this.loadAvailableProcessors();
      this.updateCompilationModeStatus();
      console.log('Project Oriented Configuration System initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Project Oriented System:', error);
      this.showNotification('Failed to initialize configuration system', 'error', 4000);
    }
  }
    
  cacheElements() {
    this.elements = {
      // Modal elements
      modal: document.getElementById('modalProjectConfig'),
      closeBtn: document.getElementById('closeProjectModal'),
      cancelBtn: document.getElementById('cancelProjectConfig'),
      saveBtn: document.getElementById('saveProjectConfig'),
      
      // File Mode elements
      fileModeToggle: document.getElementById('fileModeToggle'),
      fileModeContainer: document.getElementById('fileModeContainer'),
      
      // File management
      synthesizableDropArea: document.getElementById('synthesizableDropArea'),
      testbenchDropArea: document.getElementById('testbenchDropArea'),
      synthesizableFileList: document.getElementById('synthesizableFileList'),
      testbenchFileList: document.getElementById('testbenchFileList'),
      synthesizableEmptyState: document.getElementById('synthesizableEmptyState'),
      testbenchEmptyState: document.getElementById('testbenchEmptyState'),
      
      // Import buttons
      importSynthesizableBtn: document.getElementById('importSynthesizableBtn'),
      importTestbenchBtn: document.getElementById('importTestbenchBtn'),
      
      // Processor management
      processorsList: document.getElementById('processorsList'),
      addProcessorBtn: document.getElementById('addProcessor'),
      
      // Configuration fields
      iverilogFlags: document.getElementById('iverilogFlags'),
      projectSimuDelay: document.getElementById('projectSimuDelay'),
      showArraysCheckbox: document.getElementById('showArraysInGtkwave-project'),
      
      // Containers to hide in File Mode
      testbenchSection: document.getElementById('testbenchSection'),
      processorsSection: document.getElementById('processorsSection'),
      simulationSection: document.getElementById('simulationSection'),
      
      // UI elements
      toggleButton: document.getElementById('toggle-ui'),
      settingsButton: document.getElementById('settings'),
      processorStatus: document.getElementById('processorNameID'),
      statusText: document.getElementById('processorProjectOriented')
    };
  }
  
  setupEventListeners() {
    // Modal controls
    this.elements.closeBtn?.addEventListener('click', () => this.closeModal());
    this.elements.cancelBtn?.addEventListener('click', () => this.closeModal());
    this.elements.saveBtn?.addEventListener('click', () => this.saveConfiguration());
    
    this.elements.toggleButton?.addEventListener('click', () => {
      setTimeout(() => this.updateCompilationModeStatus(), 50);
    });

    // File Mode toggle
    this.elements.fileModeToggle?.addEventListener('change', (e) => {
      this.toggleFileMode(e.target.checked);
    });

    // Import buttons
    this.elements.importSynthesizableBtn?.addEventListener('click', () => this.handleImportClick('synthesizable'));
    this.elements.importTestbenchBtn?.addEventListener('click', () => this.handleImportClick('testbench'));
    
    // Processor management
    this.elements.addProcessorBtn?.addEventListener('click', () => this.addProcessorRow());
    this.elements.processorsList?.addEventListener('click', (e) => this.handleProcessorListClick(e));
    
    // Settings button
    this.elements.settingsButton?.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const isProjectMode = this.elements.toggleButton?.classList.contains('active');
      if (isProjectMode) {
        await this.openModal();
      }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.elements.modal?.classList.contains('show')) {
        this.closeModal();
      }
    });
    
    // Setup drag and drop
    this.setupDragAndDrop();
  }
  
  toggleFileMode(enabled) {
    this.isFileMode = enabled;
    
    // Hide/show sections based on File Mode
    const sectionsToToggle = [
      this.elements.testbenchSection,
      this.elements.processorsSection,
      this.elements.simulationSection
    ];
    
    sectionsToToggle.forEach(section => {
      if (section) {
        section.style.display = enabled ? 'none' : 'block';
      }
    });
    
    // Update UI feedback
    const fileModeLabel = this.elements.fileModeContainer?.querySelector('label');
    if (fileModeLabel) {
      fileModeLabel.style.color = enabled ? 'var(--accent-primary)' : '';
      fileModeLabel.style.fontWeight = enabled ? 'var(--font-semibold)' : '';
    }
    
    this.showNotification(
      enabled ? 'File Mode enabled - simplified configuration' : 'Full project mode enabled',
      'info',
      2000
    );
  }
  
  updateCompilationModeStatus() {
    if (!this.elements.toggleButton || !this.elements.statusText) {
      console.warn('UI toggle button or status text element not found.');
      return;
    }

    const statusElement = this.elements.statusText;
    const isProjectMode = this.elements.toggleButton.classList.contains('active');

    const newHTML = isProjectMode
      ? '<i class="fa-solid fa-lock"></i> Project Oriented'
      : '<i class="fa-solid fa-lock-open"></i> Processor Oriented';

    if (statusElement.innerHTML.trim() === newHTML.trim()) {
      return;
    }

    statusElement.style.opacity = '0';

    setTimeout(() => {
      statusElement.innerHTML = newHTML;
      statusElement.style.opacity = '1';
    }, 300);
  }

  setupDragAndDrop() {
    const dropAreas = [
      { element: this.elements.synthesizableDropArea, type: 'synthesizable' },
      { element: this.elements.testbenchDropArea, type: 'testbench' }
    ];
    
    dropAreas.forEach(({ element, type }) => {
      if (!element) return;
      
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        element.addEventListener(eventName, this.preventDefaults, false);
      });
      
      ['dragenter', 'dragover'].forEach(eventName => {
        element.addEventListener(eventName, () => this.highlightDropZone(element), false);
      });
      
      ['dragleave', 'drop'].forEach(eventName => {
        element.addEventListener(eventName, () => this.unhighlightDropZone(element), false);
      });
      
      element.addEventListener('drop', (e) => this.handleDrop(e, type), false);
    });
  }
  
  enhanceDropZones() {
    const style = document.createElement('style');
    style.textContent = `
      .file-mode-container {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-4);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        margin-bottom: var(--space-6);
      }
      
      .file-mode-switch {
        position: relative;
        display: inline-block;
        width: 48px;
        height: 24px;
      }
      
      .file-mode-switch input {
        opacity: 0;
        width: 0;
        height: 0;
      }
      
      .file-mode-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--bg-quaternary);
        transition: 0.3s;
        border-radius: 24px;
        border: 1px solid var(--border-primary);
      }
      
      .file-mode-slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 3px;
        bottom: 3px;
        background-color: var(--text-secondary);
        transition: 0.3s;
        border-radius: 50%;
      }
      
      input:checked + .file-mode-slider {
        background-color: var(--accent-primary);
        border-color: var(--accent-primary);
      }
      
      input:checked + .file-mode-slider:before {
        transform: translateX(24px);
        background-color: white;
      }
      
      .file-mode-label {
        font-size: var(--text-base);
        font-weight: var(--font-medium);
        color: var(--text-primary);
        cursor: pointer;
        user-select: none;
      }
      
      .file-drop-area {
        position: relative;
        transition: all var(--transition-normal);
      }
      
      .file-drop-area.dragover {
        transform: scale(1.02);
        box-shadow: 0 0 0 3px var(--accent-primary), var(--shadow-lg);
      }
      
      .drop-zone {
        border: 2px dashed var(--border-primary);
        border-radius: var(--radius-lg);
        padding: var(--space-8);
        text-align: center;
        background: var(--bg-tertiary);
        transition: all var(--transition-normal);
        cursor: pointer;
      }
      
      .drop-zone:hover {
        border-color: var(--accent-secondary);
        background: var(--bg-quaternary);
      }
      
      .file-list {
        margin-top: var(--space-4);
        max-height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
      }
      
      .project-file-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--space-3) var(--space-4);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
        opacity: 0;
        transform: translateX(-10px);
        animation: slideIn var(--transition-normal) forwards;
      }
      
      .project-file-item:hover {
        background: var(--bg-quaternary);
        border-color: var(--accent-secondary);
        transform: translateX(2px);
      }
      
      .project-file-item.starred {
        background: var(--accent-subtle-bg);
        border-color: var(--accent-primary);
      }
      
      @keyframes slideIn {
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }
      
      .project-icon-btn {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: transparent;
        border: none;
        border-radius: var(--radius-sm);
        color: var(--text-secondary);
        cursor: pointer;
        transition: all var(--transition-fast);
      }
      
      .project-icon-btn.star-btn.starred {
        color: var(--accent-primary);
      }
      
      .project-icon-btn.delete-btn:hover {
        background: var(--status-error-bg);
        color: var(--status-error);
      }

      #processorProjectOriented {
        transition: opacity 0.3s ease-in-out;
      }
    `;
    document.head.appendChild(style);
  }
  
  preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  highlightDropZone(dropArea) {
    dropArea.classList.add('dragover');
  }
  
  unhighlightDropZone(dropArea) {
    dropArea.classList.remove('dragover');
  }
  
  async handleDrop(e, type) {
    const droppedFiles = e.dataTransfer.files;
    
    if (!droppedFiles || droppedFiles.length === 0) {
      this.showNotification('No files dropped', 'warning', 2000);
      return;
    }
    
    const filesWithPath = [];
    
    for (let i = 0; i < droppedFiles.length; i++) {
      const file = droppedFiles[i];
      let filePath = window.electronAPI.getPathForFile(file);
      
      if (!filePath || filePath === '') {
        this.showNotification(
          `Cannot get path for "${file.name}". Try using Browse Files button.`, 
          'warning', 
          3000
        );
        continue;
      }
      
      filePath = filePath.replace(/\//g, '\\');
      
      try {
        const exists = await window.electronAPI.fileExists(filePath);
        
        if (!exists) {
          this.showNotification(`File does not exist: ${filePath}`, 'warning', 3000);
          continue;
        }
        
        filesWithPath.push({
          name: file.name,
          path: filePath,
          type: file.type || this.getMimeTypeFromExtension(file.name),
          starred: false
        });
        
      } catch (error) {
        console.error(`Error validating file:`, error);
        this.showNotification(`Error validating "${file.name}"`, 'error', 3000);
      }
    }
    
    if (filesWithPath.length > 0) {
      await this.importFiles(filesWithPath, type);
    } else {
      this.showNotification('No files could be imported. Use Browse Files button.', 'warning', 3000);
    }
  }

  async handleImportClick(type) {
    try {
      const filters = type === 'synthesizable' 
        ? [
            { name: 'Verilog Files', extensions: ['v', 'sv', 'vh'] },
            { name: 'All Files', extensions: ['*'] }
          ]
        : [
            { name: 'Verilog Files', extensions: ['v', 'sv'] },
            { name: 'GTKWave Files', extensions: ['gtkw'] },
            { name: 'All Files', extensions: ['*'] }
          ];
      
      const result = await window.electronAPI.selectFilesWithPath({
        title: `Select ${type === 'synthesizable' ? 'Synthesizable' : 'Testbench'} Files`,
        filters: filters
      });
      
      if (!result.canceled && result.files.length > 0) {
        await this.importFiles(result.files, type);
      }
    } catch (error) {
      console.error('Error selecting files:', error);
      this.showNotification('Error selecting files', 'error', 3000);
    }
  }
  
  async importFiles(files, type) {
    const validFiles = [];
    const errors = [];
    
    for (let file of files) {
      if (!file.path || file.path === '') {
        errors.push(`"${file.name}" has no path information`);
        continue;
      }
      
      const ext = file.name.toLowerCase().split('.').pop();
      const allowedExtensions = type === 'synthesizable' 
        ? ['v', 'sv', 'vh'] 
        : ['v', 'sv', 'gtkw'];
      
      if (!allowedExtensions.includes(ext)) {
        errors.push(`"${file.name}" has unsupported extension .${ext}`);
        continue;
      }
      
      const existingFiles = type === 'synthesizable' ? this.synthesizableFiles : 
                            ext === 'gtkw' ? this.gtkwFiles : this.testbenchFiles;
      
      if (existingFiles.some(f => f.path === file.path)) {
        errors.push(`"${file.name}" already exists in the project`);
        continue;
      }
      
      validFiles.push({
        name: file.name,
        path: file.path,
        type: file.type || this.getMimeTypeFromExtension(file.name),
        starred: false
      });
    }
    
    if (errors.length > 0) {
      errors.forEach(error => {
        this.showNotification(error, 'warning', 2500);
      });
    }
    
    if (validFiles.length === 0) {
      if (errors.length === 0) {
        this.showNotification('No valid files to import', 'warning', 3000);
      }
      return;
    }
    
    if (type === 'synthesizable') {
      this.synthesizableFiles.push(...validFiles);
      this.updateFileList('synthesizable');
      
      if (!this.isFileMode) {
        await this.parseAllSynthesizableFiles();
        this.refreshAllInstanceSelects();
      }
    } else {
      validFiles.forEach(file => {
        if (file.name.toLowerCase().endsWith('.gtkw')) {
          this.gtkwFiles.push(file);
        } else {
          this.testbenchFiles.push(file);
        }
      });
      this.updateFileList('testbench');
    }
    
    this.showNotification(
      `Successfully added ${validFiles.length} file(s)`, 
      'success', 
      3000
    );
  }
  
  getMimeTypeFromExtension(fileName) {
    const ext = fileName.toLowerCase().split('.').pop();
    const mimeTypes = {
      'v': 'text/x-verilog',
      'sv': 'text/x-systemverilog',
      'vh': 'text/x-verilog-header',
      'gtkw': 'application/x-gtkwave',
      'txt': 'text/plain'
    };
    return mimeTypes[ext] || 'application/octet-stream';
  }
  
  updateFileList(type) {
    const fileList = type === 'synthesizable' ? this.elements.synthesizableFileList : this.elements.testbenchFileList;
    const emptyState = type === 'synthesizable' ? this.elements.synthesizableEmptyState : this.elements.testbenchEmptyState;
    
    if (!fileList) return;
    
    fileList.innerHTML = '';
    
    if (type === 'synthesizable') {
      if (this.synthesizableFiles.length === 0) {
        if (emptyState) {
          fileList.appendChild(emptyState.cloneNode(true));
        }
      } else {
        const sortedFiles = this.getSortedFiles(this.synthesizableFiles);
        sortedFiles.forEach((file, index) => {
          const actualIndex = this.synthesizableFiles.findIndex(f => f.path === file.path);
          const fileItem = this.createFileItem(file, actualIndex, 'synthesizable');
          fileList.appendChild(fileItem);
        });
      }
    } else {
      const totalFiles = this.testbenchFiles.length + this.gtkwFiles.length;
      
      if (totalFiles === 0) {
        if (emptyState) {
          fileList.appendChild(emptyState.cloneNode(true));
        }
      } else {
        const sortedTestbench = this.getSortedFiles(this.testbenchFiles);
        sortedTestbench.forEach((file, index) => {
          const actualIndex = this.testbenchFiles.findIndex(f => f.path === file.path);
          const fileItem = this.createFileItem(file, actualIndex, 'testbench');
          fileList.appendChild(fileItem);
        });
        
        const sortedGtkw = this.getSortedFiles(this.gtkwFiles);
        sortedGtkw.forEach((file, index) => {
          const actualIndex = this.gtkwFiles.findIndex(f => f.path === file.path);
          const fileItem = this.createFileItem(file, actualIndex, 'gtkw');
          fileList.appendChild(fileItem);
        });
      }
    }
  }
  
  getSortedFiles(files) {
    return [...files].sort((a, b) => {
      if (a.starred && !b.starred) return -1;
      if (!a.starred && b.starred) return 1;
      return a.name.localeCompare(b.name);
    });
  }
  
  createFileItem(file, index, type) {
    const fileItem = document.createElement('div');
    fileItem.className = `project-file-item ${file.starred ? 'starred' : ''}`;
    fileItem.dataset.fileIndex = index;
    fileItem.dataset.fileType = type;
    
    const isStarred = file.starred || false;
    
    fileItem.innerHTML = `
      <div class="project-file-info">
        <div class="project-file-details">
          <div class="project-file-name" title="${file.path}">${file.name}</div>
        </div>
      </div>
      <div class="project-file-actions">
        <button class="project-icon-btn star-btn ${isStarred ? 'starred' : ''}" 
                data-index="${index}" 
                data-type="${type}"
                title="${isStarred ? 'Remove star' : 'Set as top-level file'}">
          <i class="fa-solid fa-star-of-life"></i>
        </button>
        <button class="project-icon-btn delete-btn" 
                data-index="${index}" 
                data-type="${type}"
                title="Remove file">
          <i class="fa-solid fa-trash"></i>
        </button>
      </div>
    `;
    
    const starBtn = fileItem.querySelector('.star-btn');
    const deleteBtn = fileItem.querySelector('.delete-btn');
    
    starBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.toggleFileStar(index, type);
    });
    
    deleteBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.removeFile(index, type);
    });
    
    return fileItem;
  }
  
  toggleFileStar(index, type) {
    let files, targetFile;
    
    if (type === 'synthesizable') {
      files = this.synthesizableFiles;
      targetFile = files[index];
    } else if (type === 'testbench') {
      files = this.testbenchFiles;
      targetFile = files[index];
    } else if (type === 'gtkw') {
      files = this.gtkwFiles;
      targetFile = files[index];
    }
    
    if (!targetFile) return;
    
    if (!targetFile.starred) {
      files.forEach(file => {
        if (file !== targetFile) {
          file.starred = false;
        }
      });
    }
    
    targetFile.starred = !targetFile.starred;
    
    setTimeout(() => {
      this.updateFileList('synthesizable');
      this.updateFileList('testbench');
    }, 100);
    
    const action = targetFile.starred ? 'selected as top-level file' : 'deselected';
    this.showNotification(`File "${targetFile.name}" ${action}`, 'success', 2000);
  }
  
  removeFile(index, type) {
    let files, isSynthesizable = false;
    
    if (type === 'synthesizable') {
      files = this.synthesizableFiles;
      isSynthesizable = true;
    } else if (type === 'testbench') {
      files = this.testbenchFiles;
    } else if (type === 'gtkw') {
      files = this.gtkwFiles;
    }
    
    if (!files || !files[index]) return;
    
    const fileItem = document.querySelector(`[data-file-index="${index}"][data-file-type="${type}"]`);
    
    if (fileItem) {
      fileItem.classList.add('file-animate-out');
      
      setTimeout(() => {
        files.splice(index, 1);
        this.updateFileList(type === 'gtkw' ? 'testbench' : type);
        
        if (isSynthesizable && !this.isFileMode) {
          this.parseAllSynthesizableFiles().then(() => {
            this.refreshAllInstanceSelects();
          });
        }
      }, 300);
    } else {
      files.splice(index, 1);
      this.updateFileList(type === 'gtkw' ? 'testbench' : type);
      
      if (isSynthesizable && !this.isFileMode) {
        this.parseAllSynthesizableFiles().then(() => {
          this.refreshAllInstanceSelects();
        });
      }
    }
  }
  
  async parseAllSynthesizableFiles() {
    this.processorInstancesMap = {};
    
    this.availableProcessors.forEach(proc => {
      this.processorInstancesMap[proc] = [];
    });
    
    const verilogFiles = this.synthesizableFiles.filter(file => 
      file.path && file.path.toLowerCase().endsWith('.v')
    );
    
    if (verilogFiles.length === 0) return;
    
    const fileReadPromises = verilogFiles.map(async (fileInfo) => {
      try {
        const fileContent = await window.electronAPI.readFile(fileInfo.path);
        return { content: fileContent, name: fileInfo.name };
      } catch (error) {
        console.error(`Error reading file ${fileInfo.path}:`, error);
        return null;
      }
    });
    
    const fileContents = await Promise.all(fileReadPromises);
    
    for (const file of fileContents) {
      if (file && file.content) {
        this.extractInstancesFromContent(file.content);
      }
    }
  }
  
  extractInstancesFromContent(content) {
    if (!content) return;
    
    const lines = content.split('\n');
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (line.startsWith('//') || line.startsWith('/*') || line.length === 0) continue;
      
      for (const processorName of this.availableProcessors) {
        const processorRegex = new RegExp(`\\b${processorName}\\b`);
        
        if (processorRegex.test(line)) {
          let instanceLine = line;
          let lineIndex = i;
          
          while (lineIndex < lines.length - 1 && !instanceLine.includes('(') && !instanceLine.includes(';')) {
            lineIndex++;
            const nextLine = lines[lineIndex].trim();
            if (nextLine && !nextLine.startsWith('//')) {
              instanceLine += ' ' + nextLine;
            }
          }
          
          const instanceRegex = new RegExp(
            `\\b${processorName}\\s*(?:#\\s*\\([^)]*\\))?\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(`
          );
          
          const match = instanceLine.match(instanceRegex);
          
          if (match && match[1]) {
            const instanceName = match[1];
            const verilogKeywords = ['module', 'endmodule', 'input', 'output', 'wire', 'reg'];
            
            if (!verilogKeywords.includes(instanceName.toLowerCase())) {
              if (!this.processorInstancesMap[processorName].includes(instanceName)) {
                this.processorInstancesMap[processorName].push(instanceName);
              }
            }
          }
        }
      }
    }
  }
  
  async loadAvailableProcessors() {
    try {
      const projectInfo = await window.electronAPI.getCurrentProject();
      
      if (projectInfo && projectInfo.projectOpen) {
        window.currentProjectPath = projectInfo.projectPath;
        this.availableProcessors = projectInfo.processors || [];
      } else {
        const currentProjectPath = window.currentProjectPath || localStorage.getItem('currentProjectPath');
        
        if (currentProjectPath) {
          const processors = await window.electronAPI.getAvailableProcessors(currentProjectPath);
          this.availableProcessors = processors || [];
        }
      }
    } catch (error) {
      console.error('Failed to load available processors:', error);
      this.availableProcessors = [];
    }
  }
  
  handleProcessorListClick(event) {
    const deleteBtn = event.target.closest('.delete-processor');
    if (deleteBtn) {
      const row = deleteBtn.closest('.modalConfig-processor-row');
      if (row) {
        const processorSelect = row.querySelector('.processor-select');
        
        if (processorSelect && processorSelect.value) {
          this.selectedProcessors.delete(processorSelect.value);
        }
        
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
          row.remove();
          this.refreshAllProcessorSelects();
        }, 300);
      }
    }
  }
  
  addProcessorRow() {
    const newRow = document.createElement('div');
    newRow.className = 'modalConfig-processor-row';
    
    newRow.innerHTML = `
      <div class="modalConfig-select-container">
        <label>Processor Type</label>
        <select class="processor-select modalConfig-select">
          <option value="">Select Processor</option>
        </select>
      </div>
      <div class="modalConfig-select-container">
        <label>Instance Name</label>
        <select class="processor-instance modalConfig-select" disabled>
          <option value="">Select Instance</option>
        </select>
      </div>
      <button class="delete-processor modalConfig-icon-btn" aria-label="Delete Processor">
        <i class="fa-solid fa-trash"></i>
      </button>
    `;
    
    const processorSelect = newRow.querySelector('.processor-select');
    const instanceSelect = newRow.querySelector('.processor-instance');
    
    this.populateAvailableProcessors(processorSelect);
    
    processorSelect.addEventListener('change', () => {
      const previousValue = processorSelect.dataset.previousValue || '';
      const newValue = processorSelect.value;
      
      if (previousValue && previousValue !== '') {
        this.selectedProcessors.delete(previousValue);
      }
      
      if (newValue && newValue !== '') {
        this.selectedProcessors.add(newValue);
        processorSelect.dataset.previousValue = newValue;
      }
      
      this.updateInstanceSelect(newValue, instanceSelect);
      this.refreshAllProcessorSelects();
    });
    
    this.elements.processorsList.appendChild(newRow);
  }
  
  populateAvailableProcessors(selectElement, selectedValue = '') {
    if (!selectElement) return;
    
    selectElement.innerHTML = '<option value="">Select Processor</option>';
    
    this.availableProcessors.forEach(processor => {
      const previousValue = selectElement.dataset.previousValue || '';
      if (!this.selectedProcessors.has(processor) || processor === previousValue || processor === selectedValue) {
        const option = document.createElement('option');
        option.value = processor;
        option.textContent = processor;
        
        if (processor === selectedValue) {
          option.selected = true;
        }
        
        selectElement.appendChild(option);
      }
    });
  }
  
  updateInstanceSelect(processorType, instanceSelectElement) {
    if (!instanceSelectElement) return;
    
    instanceSelectElement.innerHTML = '<option value="">Select Instance</option>';
    
    if (!processorType || processorType === '') {
      instanceSelectElement.disabled = true;
      return;
    }
    
    instanceSelectElement.disabled = false;
    
    const instances = this.processorInstancesMap[processorType] || [];
    
    if (instances.length === 0) {
      const noInstanceOption = document.createElement('option');
      noInstanceOption.value = '';
      noInstanceOption.textContent = 'No instances found';
      noInstanceOption.disabled = true;
      instanceSelectElement.appendChild(noInstanceOption);
      return;
    }
    
    instances.forEach(instance => {
      const option = document.createElement('option');
      option.value = instance;
      option.textContent = instance;
      instanceSelectElement.appendChild(option);
    });
  }
  
  refreshAllProcessorSelects() {
    const processorRows = this.elements.processorsList.querySelectorAll('.modalConfig-processor-row');
    
    processorRows.forEach(row => {
      const processorSelect = row.querySelector('.processor-select');
      if (processorSelect) {
        const currentValue = processorSelect.value;
        this.populateAvailableProcessors(processorSelect, currentValue);
      }
    });
  }
  
  refreshAllInstanceSelects() {
    const processorRows = this.elements.processorsList.querySelectorAll('.modalConfig-processor-row');
    
    processorRows.forEach(row => {
      const processorSelect = row.querySelector('.processor-select');
      const instanceSelect = row.querySelector('.processor-instance');
      
      if (processorSelect && instanceSelect) {
        const currentProcessor = processorSelect.value;
        const currentInstance = instanceSelect.value;
        
        if (currentProcessor) {
          this.updateInstanceSelect(currentProcessor, instanceSelect);
          
          if (currentInstance) {
            const optionExists = Array.from(instanceSelect.options).some(
              opt => opt.value === currentInstance
            );
            if (optionExists) {
              instanceSelect.value = currentInstance;
            }
          }
        }
      }
    });
  }
  
  async openModal() {
    if (!this.elements.modal) return;
    
    this.elements.modal.setAttribute('aria-hidden', 'false');
    this.elements.modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    
    await this.loadAvailableProcessors();
    await this.loadConfiguration();
    
    if (!this.isFileMode) {
      await this.parseAllSynthesizableFiles();
    }
    
    this.updateFormWithConfig();
    
    const focusable = this.elements.modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable) {
      focusable.focus();
    }
  }
  
  closeModal() {
    if (!this.elements.modal) return;
    
    this.elements.modal.setAttribute('aria-hidden', 'true');
    this.elements.modal.classList.remove('show');
    
    if (!document.querySelector('.modal-overlay[aria-hidden="false"]')) {
      document.body.style.overflow = '';
    }
  }
  
  async loadConfiguration() {
    try {
      this.currentConfig = {
        topLevelFile: '',
        testbenchFile: '',
        gtkwaveFile: '',
        processors: [],
        iverilogFlags: '',
        simuDelay: '200000',
        showArraysInGtkwave: 0
      };
      
      this.synthesizableFiles = [];
      this.testbenchFiles = [];
      this.gtkwFiles = [];
      
      let projectPath = window.currentProjectPath;
      
      if (!projectPath) {
        const projectData = await window.electronAPI.getCurrentProject();
        if (projectData && typeof projectData === 'object' && projectData.projectPath) {
          projectPath = projectData.projectPath;
          window.currentProjectPath = projectPath;
        } else if (typeof projectData === 'string') {
          projectPath = projectData;
          window.currentProjectPath = projectPath;
        }
      }
      
      if (!projectPath) {
        console.error('Project path not available');
        return;
      }
      
      // Check for File Mode config first
      const fileModeConfigPath = await window.electronAPI.joinPath(projectPath, this.FILE_MODE_CONFIG_FILENAME);
      const fileModeExists = await window.electronAPI.fileExists(fileModeConfigPath);
      
      if (fileModeExists) {
        const configContent = await window.electronAPI.readFile(fileModeConfigPath);
        this.fileModeConfig = JSON.parse(configContent);
        this.isFileMode = true;
        
        if (this.elements.fileModeToggle) {
          this.elements.fileModeToggle.checked = true;
        }
        
        await this.loadAndValidateFiles(this.fileModeConfig.synthesizableFiles, 'synthesizable');
        this.updateFileList('synthesizable');
        this.toggleFileMode(true);
        return;
      }
      
      // Load standard project config
      const configPath = await window.electronAPI.joinPath(projectPath, this.CONFIG_FILENAME);
      const configExists = await window.electronAPI.fileExists(configPath);
      
      if (configExists) {
        const configContent = await window.electronAPI.readFile(configPath);
        const configData = JSON.parse(configContent);
        this.currentConfig = configData;
        this.isFileMode = false;
        
        if (this.elements.fileModeToggle) {
          this.elements.fileModeToggle.checked = false;
        }
        
        await this.loadAndValidateFiles(configData.synthesizableFiles, 'synthesizable');
        await this.loadAndValidateFiles(configData.testbenchFiles, 'testbench');
        await this.loadAndValidateFiles(configData.gtkwFiles, 'gtkw');
        
        this.updateFileList('synthesizable');
        this.updateFileList('testbench');
        this.toggleFileMode(false);
      }
    } catch (error) {
      console.error('Error loading project configuration:', error);
    }
  }
  
  async loadAndValidateFiles(files, type) {
    if (!files || !Array.isArray(files)) return;
    
    const validFiles = [];
    
    for (const fileData of files) {
      if (fileData.path && fileData.path !== '') {
        try {
          const exists = await window.electronAPI.fileExists(fileData.path);
          
          if (exists) {
            validFiles.push({
              name: fileData.name,
              path: fileData.path,
              starred: fileData.starred || false,
              type: fileData.type || 'text/plain'
            });
          } else {
            console.warn(`File no longer exists: ${fileData.path}`);
            this.showNotification(`File not found: ${fileData.name}`, 'warning', 2000);
          }
        } catch (error) {
          console.error(`Error validating file ${fileData.path}:`, error);
        }
      }
    }
    
    if (type === 'synthesizable') {
      this.synthesizableFiles = validFiles;
    } else if (type === 'testbench') {
      this.testbenchFiles = validFiles;
    } else if (type === 'gtkw') {
      this.gtkwFiles = validFiles;
    }
  }

  updateFormWithConfig() {
    if (this.isFileMode) {
      // File Mode: minimal configuration
      this.toggleFileMode(true);
      return;
    }
    
    // Full project mode
    if (this.elements.processorsList) {
      this.elements.processorsList.innerHTML = '';
    }
    this.selectedProcessors.clear();
    
    if (this.elements.iverilogFlags && this.currentConfig.iverilogFlags) {
      this.elements.iverilogFlags.value = this.currentConfig.iverilogFlags;
    }
    
    if (this.elements.projectSimuDelay && this.currentConfig.simuDelay) {
      this.elements.projectSimuDelay.value = this.currentConfig.simuDelay;
    }
    
    if (this.elements.showArraysCheckbox && this.currentConfig.showArraysInGtkwave !== undefined) {
      this.elements.showArraysCheckbox.checked = this.currentConfig.showArraysInGtkwave === 1;
    }
    
    if (this.currentConfig.processors && this.currentConfig.processors.length > 0) {
      this.currentConfig.processors.forEach(processor => {
        this.addProcessorRow();
        const lastRow = this.elements.processorsList.querySelector('.modalConfig-processor-row:last-child');
        if (lastRow) {
          const processorSelect = lastRow.querySelector('.processor-select');
          const instanceSelect = lastRow.querySelector('.processor-instance');
          
          if (processorSelect && processor.type) {
            this.selectedProcessors.add(processor.type);
            processorSelect.dataset.previousValue = processor.type;
            
            this.populateAvailableProcessors(processorSelect, processor.type);
            processorSelect.value = processor.type;
            
            this.updateInstanceSelect(processor.type, instanceSelect);
            
            setTimeout(() => {
              if (instanceSelect && processor.instance) {
                instanceSelect.value = processor.instance;
              }
            }, 100);
          }
        }
      });
    } else {
      this.addProcessorRow();
    }
  }
  
  async saveConfiguration() {
    try {
      let projectPath = window.currentProjectPath;
      
      if (!projectPath) {
        const projectData = await window.electronAPI.getCurrentProject();
        if (projectData && typeof projectData === 'object' && projectData.projectPath) {
          projectPath = projectData.projectPath;
          window.currentProjectPath = projectPath;
        } else if (typeof projectData === 'string') {
          projectPath = projectData;
          window.currentProjectPath = projectPath;
        }
      }
      
      if (!projectPath) {
        this.showNotification('Project path not available. Cannot save configuration.', 'error', 4000);
        return;
      }
      
      if (this.isFileMode) {
        // FILE MODE SAVE LOGIC
        if (this.synthesizableFiles.length === 0) {
          this.showNotification('You must import at least one Verilog file (.v, .sv).', 'error', 4000);
          return;
        }
        
        const starredFile = this.synthesizableFiles.find(file => file.starred);
        if (!starredFile) {
          this.showNotification('You must star one file as the top-level module.', 'error', 4000);
          return;
        }
        
        const fileModeConfig = {
          topLevelFile: starredFile.path,
          synthesizableFiles: this.synthesizableFiles.map(file => ({
            name: file.name,
            path: file.path,
            starred: file.starred || false
          }))
        };
        
        const configPath = await window.electronAPI.joinPath(projectPath, this.FILE_MODE_CONFIG_FILENAME);
        await window.electronAPI.writeFile(configPath, JSON.stringify(fileModeConfig, null, 2));
        
        // Delete old project config if exists
        const oldConfigPath = await window.electronAPI.joinPath(projectPath, this.CONFIG_FILENAME);
        const oldExists = await window.electronAPI.fileExists(oldConfigPath);
        if (oldExists) {
          await window.electronAPI.deleteFileOrDirectory(oldConfigPath);
        }
        
        console.log('File Mode configuration saved:', fileModeConfig);
        this.showNotification('File Mode configuration saved successfully!', 'success', 3000);
        this.fileModeConfig = fileModeConfig;
        
      } else {
        // FULL PROJECT MODE SAVE LOGIC
        if (this.synthesizableFiles.length === 0) {
          this.showNotification('You must import at least one synthesizable file (.v, .sv).', 'error', 4000);
          return;
        }
        
        const starredSynthesizable = this.synthesizableFiles.find(file => file.starred);
        if (!starredSynthesizable) {
          this.showNotification('You must star one synthesizable file as the top-level module.', 'error', 4000);
          return;
        }

        if (this.testbenchFiles.length === 0) {
          this.showNotification('You must import at least one testbench file (.v, .sv).', 'error', 4000);
          return;
        }
        
        const starredTestbench = this.testbenchFiles.find(file => file.starred);
        if (!starredTestbench) {
          this.showNotification('You must star one file as the main testbench.', 'error', 4000);
          return;
        }
        
        const starredGtkw = this.gtkwFiles.find(file => file.starred);
        
        const processors = [];
        const processorRows = this.elements.processorsList.querySelectorAll('.modalConfig-processor-row');
        
        processorRows.forEach(row => {
          const processorSelect = row.querySelector('.processor-select');
          const instanceSelect = row.querySelector('.processor-instance');
          
          if (processorSelect && instanceSelect) {
            const processorType = processorSelect.value;
            const instanceName = instanceSelect.value;
            
            if (processorType && processorType !== '' && instanceName && instanceName !== '') {
              processors.push({
                type: processorType,
                instance: instanceName
              });
            }
          }
        });
        
        const iverilogFlagsValue = this.elements.iverilogFlags ? this.elements.iverilogFlags.value : '';
        const simuDelayValue = this.elements.projectSimuDelay ? this.elements.projectSimuDelay.value : '200000';
        const showArraysValue = this.elements.showArraysCheckbox && this.elements.showArraysCheckbox.checked ? 1 : 0;
        
        const config = {
          topLevelFile: starredSynthesizable.path,
          testbenchFile: starredTestbench.path,
          gtkwaveFile: starredGtkw ? starredGtkw.path : '',
          synthesizableFiles: this.synthesizableFiles.map(file => ({
            name: file.name,
            path: file.path,
            starred: file.starred || false
          })),
          testbenchFiles: this.testbenchFiles.map(file => ({
            name: file.name,
            path: file.path,
            starred: file.starred || false
          })),
          gtkwFiles: this.gtkwFiles.map(file => ({
            name: file.name,
            path: file.path,
            starred: file.starred || false
          })),
          processors: processors,
          iverilogFlags: iverilogFlagsValue,
          simuDelay: simuDelayValue,
          showArraysInGtkwave: showArraysValue
        };
        
        const configPath = await window.electronAPI.joinPath(projectPath, this.CONFIG_FILENAME);
        await window.electronAPI.writeFile(configPath, JSON.stringify(config, null, 2));
        
        // Delete file mode config if exists
        const fileModeConfigPath = await window.electronAPI.joinPath(projectPath, this.FILE_MODE_CONFIG_FILENAME);
        const fileModeExists = await window.electronAPI.fileExists(fileModeConfigPath);
        if (fileModeExists) {
          await window.electronAPI.deleteFileOrDirectory(fileModeConfigPath);
        }
        
        console.log('Project configuration saved:', config);
        this.showNotification('Project configuration saved successfully!', 'success', 3000);
        this.currentConfig = config;
        await this.updateProcessorStatus();
      }
      
      this.closeModal();
      
      // Trigger file tree refresh
      if (typeof window.refreshProjectFiles === 'function') {
        window.refreshProjectFiles();
      }
      
    } catch (error) {
      console.error('Error saving project configuration:', error);
      this.showNotification('Failed to save project configuration. Please try again.', 'error', 4000);
    }
  }
  
  async updateProcessorStatus() {
    const el = this.elements.processorStatus;
    if (!el) return;
    
    el.style.opacity = '0';
    
    await new Promise(resolve => setTimeout(resolve, 300));
    
    if (this.currentConfig?.processors?.length > 0) {
      const types = this.currentConfig.processors.map(p => p.type);
      const unique = [...new Set(types)];
      const testbench = this.currentConfig.testbenchFile ? this.currentConfig.testbenchFile.split('/').pop().split('\\').pop() : 'None';
      
      el.innerHTML = `${unique.join(' | ')}&nbsp;<i class="fa-solid fa-gear"></i> ${testbench}`;
      el.classList.add('has-processors');
    } else {
      el.innerHTML = `<i class="fa-solid fa-xmark" style="color: #FF3131"></i> No Processor Configured`;
      el.classList.remove('has-processors');
    }
    
    el.style.opacity = '1';
  }
  
  showNotification(message, type = 'info', duration = 3000) {
    if (typeof window.showNotification === 'function') {
      window.showNotification(message, type, duration);
      return;
    }
    
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
      notificationContainer = document.createElement('div');
      notificationContainer.id = 'notification-container';
      notificationContainer.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        max-width: 100%;
        width: 350px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
      `;
      document.body.appendChild(notificationContainer);
    }
    
    const iconMap = {
      error: { icon: 'fa-circle-exclamation', color: 'var(--status-error)' },
      success: { icon: 'fa-circle-check', color: 'var(--status-success)' },
      warning: { icon: 'fa-triangle-exclamation', color: 'var(--status-warning)' },
      info: { icon: 'fa-circle-info', color: 'var(--accent-primary)' }
    };
    
    const { icon, color } = iconMap[type] || iconMap.info;
    
    const notification = document.createElement('div');
    notification.style.cssText = `
      background-color: var(--bg-elevated);
      border-left: 4px solid ${color};
      color: var(--text-primary);
      padding: var(--space-4);
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      opacity: 0;
      transform: translateX(20px);
      transition: all var(--transition-normal);
    `;
    
    notification.innerHTML = `
      <div style="display: flex; align-items: center; gap: var(--space-3); margin-bottom: var(--space-2);">
        <i class="fa-solid ${icon}" style="color: ${color}; font-size: var(--text-xl);"></i>
        <div style="flex-grow: 1;">
          <div style="font-weight: var(--font-semibold); font-size: var(--text-base);">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
        </div>
        <div class="close-btn" style="cursor: pointer; font-size: var(--text-lg);">
          <i class="fa-solid fa-xmark" style="opacity: 0.7;"></i>
        </div>
      </div>
      <div style="padding-left: calc(var(--text-xl) + var(--space-3)); font-size: var(--text-sm);">
        ${message}
      </div>
      <div class="progress-bar" style="position: absolute; bottom: 0; left: 0; height: 3px; width: 100%; background-color: ${color}; transform-origin: left; transform: scaleX(1);"></div>
    `;
    
    notificationContainer.prepend(notification);
    
    requestAnimationFrame(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateX(0)';
    });
    
    const progressBar = notification.querySelector('.progress-bar');
    progressBar.style.transition = `transform ${duration}ms linear`;
    
    setTimeout(() => {
      progressBar.style.transform = 'scaleX(0)';
    }, 10);
    
    const closeBtn = notification.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => this.closeNotification(notification));
    
    const timeoutId = setTimeout(() => this.closeNotification(notification), duration);
    
    notification.addEventListener('mouseenter', () => {
      progressBar.style.transitionProperty = 'none';
      clearTimeout(timeoutId);
    });
    
    notification.addEventListener('mouseleave', () => {
      const remainingTime = duration * (parseFloat(getComputedStyle(progressBar).transform.split(', ')[0].split('(')[1]) || 0);
      if (remainingTime > 0) {
        progressBar.style.transition = `transform ${remainingTime}ms linear`;
        progressBar.style.transform = 'scaleX(0)';
        setTimeout(() => this.closeNotification(notification), remainingTime);
      } else {
        this.closeNotification(notification);
      }
    });
  }
  
  closeNotification(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateX(20px)';
    
    setTimeout(() => {
      if (element.parentNode) {
        element.parentNode.removeChild(element);
        
        const container = document.getElementById('notification-container');
        if (container && container.children.length === 0) {
          container.remove();
        }
      }
    }, 300);
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.projectOrientedManager = new ProjectOrientedManager();
});

// Export for external access
window.projectOrientedConfig = {
  openModal: () => window.projectOrientedManager?.openModal(),
  saveConfig: () => window.projectOrientedManager?.saveConfiguration(),
  loadConfig: () => window.projectOrientedManager?.loadConfiguration()
};