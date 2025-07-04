<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { JSONEditor } from 'svelte-jsoneditor';
  // import { fetchVendors, createVendor, updateVendor, deleteVendor, fetchSummaryFormat, updateSummaryFormat, fetchVendor } from '$lib/apis/vendors';
  // 임시로 items API 사용 (vendors API로 분리 필요)
  import {
    fetchCustomers,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    fetchSummaryFormat,
    updateSummaryFormat,
    fetchCustomer
  } from '$lib/apis/customers';
  import RecursiveTreeNode from '$lib/components/common/RecursiveTreeNode.svelte';
  import { toastMsg } from '$lib/stores/toast';

  let customers: any[] = [];
  let loading = true;
  let selectedCustomer: any = null;
  let editing = false;
  let saveMsg: string | null = null;
  let errorMsg = '';
  let jsonContent: any = {};
  let editingCustomer: any = null;
  let addingCustomer = false;

  let treeData: {
    nodes: Array<{
      id: number;
      name: string;
      nodeKind: 'tree' | 'spec';
      type?: 'number' | 'string' | 'link' | 'custom';
      value?: string;
      children?: any[];
    }>;
  } = {
    nodes: []
  };

  let newCustomer = {
    name: '',
    description: '',
    created_at: new Date().toISOString().split('T')[0]
  };

  onMount(async () => {
    try {
      loading = true;
      const rawCustomers = await fetchCustomers();
      // uid를 id로 매핑
      customers = rawCustomers.map((customer: any) => ({
        ...customer,
        id: customer.uid || customer.id
      }));
    } catch (e: any) {
      errorMsg = e.message ?? '고객 로드 실패';
      customers = [];
    } finally {
      loading = false;
    }
  });

  function handleAddNode(parent: any = null) {
    const newNode = {
      id: Date.now() + Math.random(),
      name: '',
      nodeKind: 'tree' as 'tree' | 'spec',
      type: 'string' as 'number' | 'string' | 'link' | 'custom',
      children: [] as any[]
    };
    if (parent) {
      parent.children = [...(parent.children || []), newNode];
    } else {
      treeData.nodes = [...treeData.nodes, newNode];
    }
    treeData = { ...treeData };
    jsonContent = treeToJSON();
  }

  function handleRemoveNode(parent: any, index: number) {
    if (parent) {
      parent.children = parent.children.filter((_: any, i: number) => i !== index);
    } else {
      treeData.nodes = treeData.nodes.filter((_: any, i: number) => i !== index);
    }
    treeData = { ...treeData };
    jsonContent = treeToJSON();
  }

  function handleTypeToggle(node: any, parent: any, index: number) {
    if (node.nodeKind === 'tree') {
      node.nodeKind = 'spec';
      node.type = 'string';
      node.value = '';
      delete node.children;
    } else {
      node.nodeKind = 'tree';
      delete node.type;
      delete node.value;
      node.children = [];
    }
    if (parent && typeof index === 'number') {
      parent.children[index] = { ...node };
    } else if (typeof index === 'number') {
      treeData.nodes[index] = { ...node };
    }
    treeData = { ...treeData };
    jsonContent = treeToJSON();
  }

  function handleSpecTypeChange(node: any, type: string, parent: any, index: number) {
    node.type = type;
    if (parent && typeof index === 'number') {
      parent.children[index] = { ...node };
    } else {
      const nodeIndex = treeData.nodes.findIndex((n: any) => n.id === node.id);
      if (nodeIndex !== -1) {
        treeData.nodes[nodeIndex] = { ...node };
      }
    }
    treeData = { ...treeData };
    jsonContent = treeToJSON();
  }

  function findNodeAndParent(nodes: any[], targetId: string, parent: any = null, parentIndex: number = -1): { node: any, parent: any, index: number } | null {
    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      if (node.id === targetId) {
        return { node, parent, index: i };
      }
      if (node.children && node.children.length > 0) {
        const result = findNodeAndParent(node.children, targetId, node, i);
        if (result) return result;
      }
    }
    return null;
  }

  function handleNodeChange(node: any, changeType: string, parent: any, index: number) {
    if (changeType === 'tree' || changeType === 'spec') {
      const result = findNodeAndParent(treeData.nodes, node.id);
      if (result) {
        if (result.parent) {
          result.parent.children[result.index] = node;
        } else {
          treeData.nodes[result.index] = node;
        }
        treeData = { ...treeData };
        jsonContent = treeToJSON();
      }
    } else {
      const result = findNodeAndParent(treeData.nodes, node.id);
      if (result) {
        if (result.parent) {
          handleSpecTypeChange(node, changeType, result.parent, result.index);
        } else {
          handleSpecTypeChange(node, changeType, null, result.index);
        }
      }
    }
  }

  function treeToJSON() {
    function convertNode(node: any): any {
      if (node.nodeKind === 'spec') {
        return { type: node.type };
      } else {
        const result: any = {};
        (node.children ?? []).forEach((child: any) => {
          if (child.name) result[child.name] = convertNode(child);
        });
        return result;
      }
    }
    const result: any = {};
    (treeData.nodes ?? []).forEach(node => {
      if (node.name) result[node.name] = convertNode(node);
    });
    return result;
  }

  function jsonToTree(json: any) {
    function convertToNode(key: string, value: any): any {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        const node = {
          id: Date.now() + Math.random(),
          name: key,
          type: 'tree' as 'tree' | 'spec',
          children: []
        };
        for (const [childKey, childValue] of Object.entries(value)) {
          node.children.push(convertToNode(childKey, childValue));
        }
        return node;
      } else {
        return {
          id: Date.now() + Math.random(),
          name: key,
          type: 'spec' as 'tree' | 'spec',
          value: String(value)
        };
      }
    }
    const nodes: any[] = [];
    for (const [key, value] of Object.entries(json)) {
      nodes.push(convertToNode(key, value));
    }
    return { nodes };
  }

  function onNodeNameInput(node) {
    jsonContent = treeToJSON();
  }

  $: jsonContent = treeToJSON();

  function cancelEdit() {
    editingCustomer = null;
    addingCustomer = false;
    treeData = { nodes: [] };
  }

  function editCustomer(customer: any) {
    editingCustomer = { ...customer };
    if (customer.properties) {
      treeData = jsonToTree(customer.properties);
    } else {
      treeData = { nodes: [] };
    }
    jsonContent = treeToJSON();
  }

  async function saveEdit() {
    if (!editingCustomer) return;
    const propertiesData = treeToJSON();
    try {
      if (addingCustomer) {
        const created = await createCustomer({
          name: editingCustomer.name,
          description: editingCustomer.description,
          status: editingCustomer.status || 'active',
          created_at: editingCustomer.created_at
        });
        await updateCustomer(created.id, {
          name: editingCustomer.name,
          description: editingCustomer.description,
          status: editingCustomer.status || 'active',
          properties: propertiesData
        });
        addingCustomer = false;
      } else {
        // ID가 없으면 에러 처리
        if (!editingCustomer.id) {
          errorMsg = '고객 ID가 없습니다. 고객을 다시 선택해주세요.';
          return;
        }
        await updateCustomer(editingCustomer.id, {
          name: editingCustomer.name,
          description: editingCustomer.description,
          status: editingCustomer.status || 'active',
          properties: propertiesData
        });
      }
      customers = await fetchCustomers();
      toastMsg.set('저장되었습니다!');
      errorMsg = '';
      setTimeout(() => { toastMsg.set(''); }, 2000);
    } catch (e: any) {
      errorMsg = e.message ?? '저장 실패';
      toastMsg.set('');
    }
  }

  function handleAddCustomerClick() {
    addingCustomer = true;
    editingCustomer = {
      name: '',
      description: '',
      status: 'active',
      created_at: new Date().toISOString().split('T')[0]
    };
    treeData = { nodes: [] };
    jsonContent = treeToJSON();
    errorMsg = '';
  }

  async function handleDeleteCustomer(customerId: string) {
    try {
      await deleteCustomer(customerId);
      customers = await fetchCustomers();
      toastMsg.set('삭제되었습니다!');
      setTimeout(() => { toastMsg.set(''); }, 2000);
    } catch (e: any) {
      errorMsg = e.message ?? '삭제 실패';
      toastMsg.set('');
    }
  }
</script>

{#if saveMsg}
  <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 text-green-700 bg-green-100 border border-green-300 px-6 py-2 rounded shadow">
    {saveMsg}
  </div>
{/if}

<div class="flex gap-6">
  <div class="w-2/3">
    <!-- 왼쪽: 고객 목록 -->
    <div class="flex gap-8 h-full">
      <div class="w-1/4">
        <h2 class="font-bold mb-2">고객 목록</h2>
        <div class="mb-2">
          <button class="btn btn-primary btn-sm" on:click={handleAddCustomerClick}>새 고객 추가</button>
        </div>

        {#if errorMsg}
          <div class="text-red-600 mb-2">{errorMsg}</div>
        {/if}

        {#if loading}
          <div>Loading...</div>
        {:else}
          <div class="space-y-2 max-h-96 overflow-y-auto">
            {#each customers as customer}
              <div class="p-3 border rounded cursor-pointer hover:bg-gray-50 {editingCustomer?.id === customer.id ? 'bg-blue-50 border-blue-300' : ''}" 
                   on:click={() => editCustomer(customer)}>
                <div class="font-medium">{customer.name || '이름 없음'}</div>
                <div class="text-sm text-gray-600">{customer.description || '설명 없음'}</div>
                <div class="text-sm text-gray-500">{customer.created_at || '날짜 없음'}</div>
                <div class="flex gap-1 mt-2">
                  <button class="btn btn-xs" on:click|stopPropagation={() => editCustomer(customer)}>수정</button>
                  <button class="btn btn-xs btn-error" on:click|stopPropagation={() => handleDeleteCustomer(customer.id)}>삭제</button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- 중앙: 동적 트리 폼 -->
      {#if editingCustomer}
        <div class="flex-1">
          <div class="flex justify-between items-center mb-4">
            <h2 class="font-bold">{addingCustomer ? '고객 추가' : `고객 수정: ${editingCustomer.name}`}</h2>
            <div class="flex gap-2">
              <button class="btn btn-outline" on:click={cancelEdit}>취소</button>
              <button class="btn btn-primary" on:click={() => { jsonContent = treeToJSON(); saveEdit(); }}>저장</button>
            </div>
          </div>
          {#if saveMsg}
            <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 text-green-700 bg-green-100 border border-green-300 px-6 py-2 rounded shadow">
              {saveMsg}
            </div>
          {/if}
          {#if errorMsg}
            <div class="text-red-600 mb-2 p-2 bg-red-50 rounded">{errorMsg}</div>
          {/if}

          <div class="border rounded p-4">
            <div class="mb-3">
              <label class="block text-sm font-medium mb-1">고객명</label>
              <input type="text" bind:value={editingCustomer.name} class="w-full p-2 border rounded" on:input={() => { editingCustomer = { ...editingCustomer }; jsonContent = treeToJSON(); }} />
            </div>
            <div class="mb-3">
              <label class="block text-sm font-medium mb-1">설명</label>
              <input type="text" bind:value={editingCustomer.description} class="w-full p-2 border rounded" on:input={() => { editingCustomer = { ...editingCustomer }; jsonContent = treeToJSON(); }} />
            </div>
            <div class="mb-3">
              <label class="block text-sm font-medium mb-1">상태</label>
              <select bind:value={editingCustomer.status} class="w-full p-2 border rounded">
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
              </select>
            </div>
          </div>
          <div class="border rounded p-4 mt-4">
            <div class="flex justify-between items-center mb-3">
              <h3 class="font-semibold">Summary Format</h3>
              <button class="btn btn-xs btn-primary" on:click={() => handleAddNode()}>+ 노드 추가</button>
            </div>
            {#each treeData.nodes ?? [] as node, nodeIndex}
              <RecursiveTreeNode
                node={node}
                parent={null}
                onAdd={handleAddNode}
                onRemove={handleRemoveNode}
                onTypeChange={(node, changeType) => handleNodeChange(node, changeType, null, nodeIndex)}
                index={nodeIndex}
                onNodeNameInput={(node) => onNodeNameInput(node)}
              />
            {/each}
          </div>
        </div>
      {:else}
        <div class="text-gray-500">고객을 선택하여 포맷을 편집하세요.</div>
      {/if}
    </div>
  </div>
  <div class="w-1/3">
    <h3 class="font-bold mb-2">JSON 미리보기</h3>
    {#if editingCustomer}
      <div class="mb-2 text-xs text-gray-500">
        마지막 업데이트: {new Date().toLocaleTimeString()}
      </div>
      <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">{JSON.stringify(jsonContent, null, 2)}</pre>
    {:else}
      <div class="text-gray-400">고객을 선택하여 JSON을 확인하세요.</div>
    {/if}
  </div>
</div>
