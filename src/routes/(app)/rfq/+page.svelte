<script lang="ts">
  import { onMount } from 'svelte';
  import { fetchRFQs } from '$lib/apis/rfq';
  import { toastMsg } from '$lib/stores/toast';

  let rfqs: any[] = [];
  let loading = true;
  let errorMsg = '';

  // 추가, 수정, 삭제 핸들러 (스텁)
  function addRFQ() { alert('RFQ 추가 기능은 추후 구현됩니다.'); }
  function editRFQ(rfq: any) { alert('RFQ 수정 기능은 추후 구현됩니다.'); }
  function deleteRFQ(rfq: any) { alert('RFQ 삭제 기능은 추후 구현됩니다.'); }

  onMount(async () => {
    try {
      loading = true;
      rfqs = await fetchRFQs();
    } catch (e: any) {
      errorMsg = e.message ?? '데이터 로드 실패';
      rfqs = [];
    } finally {
      loading = false;
    }
  });
</script>

<div class="flex flex-col h-full bg-white dark:bg-gray-900">
  <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
    <h1 class="text-xl font-semibold text-gray-900 dark:text-white">RFQ Management</h1>
  </div>
  <div class="flex-1 p-4 overflow-auto">
    <div class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-900 dark:text-white">RFQ List</h2>
        <button class="btn btn-primary btn-sm" on:click={addRFQ}>추가</button>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
        {#if loading}
          <div class="p-4 text-center text-gray-500 dark:text-gray-400">Loading...</div>
        {:else if rfqs.length === 0}
          <div class="p-4 text-center text-gray-500 dark:text-gray-400">No RFQs found. Create a new RFQ to get started.</div>
        {:else}
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm border-collapse">
              <thead>
                <tr class="bg-gray-50 dark:bg-gray-850">
                  <th class="px-4 py-2 border-b text-left font-semibold">이름</th>
                  <th class="px-4 py-2 border-b text-left font-semibold">고객</th>
                  <th class="px-4 py-2 border-b text-left font-semibold">프로그램</th>
                  <th class="px-4 py-2 border-b text-left font-semibold">설명</th>
                  <th class="px-4 py-2 border-b text-left font-semibold">액션</th>
                </tr>
              </thead>
              <tbody>
                {#each rfqs as rfq}
                  <tr class="hover:bg-gray-100 dark:hover:bg-gray-850 transition">
                    <td class="px-4 py-2 border-b">{rfq.name || rfq.title}</td>
                    <td class="px-4 py-2 border-b">{rfq.customer_name || 'N/A'}</td>
                    <td class="px-4 py-2 border-b">{rfq.program_name || 'N/A'}</td>
                    <td class="px-4 py-2 border-b">{rfq.description || 'N/A'}</td>
                    <td class="px-4 py-2 border-b">
                      <button class="btn btn-xs mr-1" on:click={() => editRFQ(rfq)}>수정</button>
                      <button class="btn btn-xs btn-error" on:click={() => deleteRFQ(rfq)}>삭제</button>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div> 