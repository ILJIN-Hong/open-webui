<!-- RFQ Management Page Component -->
<script lang="ts">
    import { ChevronLeft, FileText, Upload, Users, Package, Scale } from 'lucide-svelte';
    import { goto } from '$app/navigation';
    let activeTab = 'list'; // Default tab
    const tabs = [
        { id: 'list', label: 'RFQ List', icon: FileText },
        { id: 'upload', label: 'Upload', icon: Upload },
        { id: 'customers', label: 'Customer Management', icon: Users },
        { id: 'program', label: 'Program Management', icon: Package },
        { id: 'compare', label: 'Compare', icon: Scale }
    ];
    export let showBackButton = true;
    export let onClose = () => {};
</script>

<nav class="flex gap-2 border-b p-2 bg-white dark:bg-gray-900">
  {#each tabs as tab}
    <a
      class="px-3 py-1 rounded-t cursor-pointer {activeTab === tab.id ? 'bg-blue-100 font-bold' : 'hover:bg-gray-100'}"
      on:click={() => {
        activeTab = tab.id;
        if (tab.id === 'customers') goto('/rfq/customers');
        else if (tab.id === 'program') goto('/rfq/program');
        // 다른 탭 라우팅 필요시 추가
      }}
    >
      <svelte:component this={tab.icon} class="inline w-4 h-4 mr-1" />
      {tab.label}
    </a>
  {/each}
</nav>

<div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
  <div class="flex items-center gap-2">
    {#if showBackButton}
      <button class="btn btn-ghost btn-sm" on:click={onClose}>
        <ChevronLeft class="w-4 h-4" />
      </button>
    {/if}
    <h1 class="text-xl font-semibold">RFQ Management</h1>
  </div>
</div>

<div class="flex justify-between items-center">
  <div class="flex-1 p-4">
    <slot />
  </div>
</div>

<style>
    /* Add any additional styles here */
</style> 