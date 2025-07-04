<script lang="ts">
  import { FolderOpen } from 'lucide-svelte';
  import { onMount, onDestroy } from 'svelte';
  let uploadFolder = '';
  let autoUploadInterval = '10min';
  const intervals = ['5min', '10min', '30min', '1hour'];
  let manualFolderInput = '';

  let folderInput: HTMLInputElement;
  let fileInput: HTMLInputElement;

  const RAG_BASE_URL = 'http://192.168.141.235:9000';

  let uploadStatus = 'Ready';
  let progress = 0;
  let totalFiles = 0;
  let processedFiles = 0;
  let pollingInterval: any = null;
  let uploadMessage = '';
  let currentFile = '';
  let fileIndex = 0;
  let currentPage = 0;
  let totalPages = 0;

  async function uploadFolderToRAG(folderPath: string) {
    console.log('uploadFolderToRAG 실행', folderPath);
    const formData = new FormData();
    formData.append('folder_path', folderPath);
    uploadStatus = 'Processing';
    uploadMessage = '업로드 시작됨';
    try {
      const res = await fetch(`${RAG_BASE_URL}/api/folders/upload`, {
        method: 'POST',
        body: formData
      });
      console.log('fetch 결과', res);
    } catch (e) {
      uploadMessage = '폴더 업로드 실패: ' + (e instanceof Error ? e.message : e);
      uploadStatus = 'Error';
      console.log('업로드 에러', e);
    }
  }

  function openManualFolderDialog() {
    manualFolderInput = '';
  }
  function openFileDialog() {
    fileInput.value = '';
    fileInput.click();
  } 
  function handleManualFolderSubmit() {
    console.log('업로드 버튼 클릭됨', uploadStatus, manualFolderInput);
    if (uploadStatus === 'Processing') {
      uploadMessage = '업로드가 진행 중입니다. 완료 후 다시 시도해주세요.';
      return;
    }
    if (manualFolderInput.trim()) {
      console.log('업로드 함수 호출!');
      uploadFolderToRAG(manualFolderInput.trim());
    } else {
      console.log('폴더 입력값 없음');
    }
  }
  function handleFileChange(e: Event) {
    const files = (e.target as HTMLInputElement).files;
    if (files) {
      alert('파일 업로드: ' + Array.from(files).map((f: any) => f.name).join(', '));
    }
  }

  function handleFolderChange(e: Event) {
    const files = (e.target as HTMLInputElement).files;
    if (files) {
      alert('폴더 업로드: ' + Array.from(files).map((f: any) => f.name).join(', '));
    }
  }

  async function pollServerStatus() {
    try {
      const res = await fetch(`${RAG_BASE_URL}/api/folders/status`);
      if (!res.ok) throw new Error('상태 조회 실패');
      const { status, total, processed, message, current_file, file_index, total_files, current_page, total_pages } = await res.json();
      uploadStatus = status || 'Ready';
      totalFiles = total_files || total || 0;
      fileIndex = file_index || processed || 0;
      currentFile = current_file || '';
      currentPage = current_page || 0;
      totalPages = total_pages || 0;
      progress = totalFiles > 0 ? Math.round((fileIndex / totalFiles) * 100) : 0;
      if (message) {
        uploadMessage = message;
      }
    } catch (e) {
      uploadStatus = 'Error';
      progress = 0;
      totalFiles = 0;
      fileIndex = 0;
      currentFile = '';
      currentPage = 0;
      totalPages = 0;
      uploadMessage = '상태 조회 실패';
    }
  }

  onMount(() => {
    pollServerStatus();
    pollingInterval = setInterval(pollServerStatus, 1000);
  });
  onDestroy(() => {
    if (pollingInterval) clearInterval(pollingInterval);
  });
</script>

<div class="flex flex-col h-full bg-white dark:bg-gray-900">
  <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
    <h1 class="text-xl font-semibold text-gray-900 dark:text-white">RFQ Management</h1>
  </div>
  <div class="flex-1 p-4 overflow-auto">
    <div class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-900 dark:text-white">RFQ Upload</h2>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div class="divide-y divide-gray-200 dark:divide-gray-800">
          <!-- 기본 업로드 폴더 -->
          <div class="flex items-center justify-between py-4 group hover:bg-gray-50 dark:hover:bg-gray-850 transition px-4">
            <div class="font-medium text-gray-800 dark:text-gray-100 w-56">기본 업로드 폴더</div>
            <div class="flex items-center gap-2 flex-1 min-w-[300px] w-full justify-start">
              <input
                class="input input-bordered flex-1 truncate text-base px-4 py-2"
                type="text"
                bind:value={uploadFolder}
                placeholder="폴더를 입력하세요"
                style="font-family:monospace; min-width: 300px; font-size: 1rem;"
              />
            </div>
          </div>
          <!-- 자동 업데이트 시간 -->
          <div class="flex items-center justify-between py-4 group hover:bg-gray-50 dark:hover:bg-gray-850 transition px-4">
            <div class="font-medium text-gray-800 dark:text-gray-100 w-56">자동 업데이트 시간</div>
            <select class="select select-bordered w-48 text-base px-4 py-2" style="height: 44px; font-size: 1rem;" bind:value={autoUploadInterval}>
              {#each intervals as interval}
                <option value={interval}>{interval}</option>
              {/each}
            </select>
          </div>
          <!-- 수동 업로드 -->
          <div class="flex items-center justify-between py-4 group hover:bg-gray-50 dark:hover:bg-gray-850 transition px-4">
            <div class="font-medium text-gray-800 dark:text-gray-100 w-56">수동 업로드</div>
            <div class="flex flex-row items-center gap-2 w-full min-w-[300px]">
              <input
                type="text"
                class="input input-bordered flex-1 truncate text-base px-4 py-2"
                bind:value={manualFolderInput}
                placeholder="폴더를 입력하세요"
                style="font-family:monospace; min-width: 300px; font-size: 1rem;"
                on:keydown={(e) => e.key === 'Enter' && handleManualFolderSubmit()}
              />
              <button 
                class="text-xs px-3 py-1.5 transition rounded-lg font-medium {uploadStatus === 'Processing' ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800'}" 
                style="height:34px; min-width:150px;" 
                on:click={handleManualFolderSubmit}
                disabled={uploadStatus === 'Processing'}
              >
                {uploadStatus === 'Processing' ? '업로드 중...' : '폴더 업로드'}
              </button>
              <button class="text-xs px-3 py-1.5 bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-lg font-medium" style="height:34px; min-width:150px;" on:click={openFileDialog}>파일 업로드</button>
            </div>
            <input
              type="file"
              multiple
              bind:this={folderInput}
              class="hidden"
              on:change={handleFolderChange}
            />
            <input
              type="file"
              multiple
              bind:this={fileInput}
              class="hidden"
              on:change={handleFileChange}
            />
          </div>
          <!-- 드래그 앤 드롭 영역 -->
          <div class="p-8 text-center">
            <p class="text-gray-500 dark:text-gray-400">여기에 파일이나 폴더를 드래그하세요</p>
          </div>
        </div>
      </div>

      <!-- 서버 상태 표시 셀 -->
      <div class="p-6 text-center rounded-lg shadow mt-4 w-full max-w-lg mx-auto"
           style="background: #f9fafb; border: 1px solid #e5e7eb;">
        <div class="text-lg font-semibold mb-2">서버 상태</div>
        <div class="mt-2">
          {#if uploadStatus === 'Ready'}
            <span class="text-gray-500">Ready</span>
          {:else if uploadStatus === 'Processing' || uploadStatus === '진행 중'}
            <span class="text-blue-600 font-bold">진행 중</span>
            <!-- 파일 기준 프로그레스 바 -->
            <div class="mt-4 text-left">
              <div class="text-xs text-gray-700 mb-1">파일 저장 진행률</div>
              <div class="w-full bg-gray-200 rounded h-4">
                <div class="bg-blue-500 h-4 rounded" style="width: {totalFiles > 0 ? Math.round((fileIndex / totalFiles) * 100) : 0}%"></div>
              </div>
              <div class="text-xs mt-1 text-blue-700">{fileIndex} / {totalFiles} 파일 ({totalFiles > 0 ? Math.round((fileIndex / totalFiles) * 100) : 0}%)</div>
            </div>
            <!-- 페이지 기준 프로그레스 바 -->
            <div class="mt-4 text-left">
              <div class="text-xs text-gray-700 mb-1">페이지 저장 진행률</div>
              <div class="w-full bg-gray-200 rounded h-4">
                <div class="bg-green-500 h-4 rounded" style="width: {totalPages > 0 ? Math.round((currentPage / totalPages) * 100) : 0}%"></div>
              </div>
              <div class="text-xs mt-1 text-green-700">{currentPage} / {totalPages} 페이지 ({totalPages > 0 ? Math.round((currentPage / totalPages) * 100) : 0}%)</div>
            </div>
            <!-- 현재 파일명 -->
            {#if currentFile}
              <div class="text-xs mt-2 text-gray-600">현재 파일: {currentFile}</div>
            {/if}
          {:else if uploadStatus === 'Done' || uploadStatus === '완료'}
            <span class="text-green-600 font-bold">업로드 완료!</span>
          {:else if uploadStatus === 'Error'}
            <span class="text-red-600 font-bold">Error</span>
            <div class="text-red-500 text-xs mt-1">상태 조회 실패</div>
          {:else}
            <span class="text-gray-400">{uploadStatus}</span>
          {/if}
        </div>
        {#if uploadMessage}
          <div class="mt-2 text-sm {uploadMessage.startsWith('업로드 완료') ? 'text-green-600' : 'text-red-600'}">
            {uploadMessage}
          </div>
        {/if}
      </div>
    </div>
  </div>
</div> 