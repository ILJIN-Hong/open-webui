<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { JSONEditor } from 'svelte-jsoneditor';
  // 기본 라이트‑테마 CSS는 번들에 포함되어 있으므로 별도 import 불필요.
  // 다크·기타 테마가 필요하다면 아래 예시처럼 사용하세요.
  // import 'svelte-jsoneditor/themes/jse-theme-dark.css';

  import {
    fetchPrograms,
    createProgram,
    updateProgram,
    deleteProgram,
    fetchSummaryFormat,
    updateSummaryFormat,
    fetchProgram
  } from '$lib/apis/program';

  import RecursiveTreeNode from '$lib/components/common/RecursiveTreeNode.svelte';
  import { toastMsg } from '$lib/stores/toast';

  let programs: any[] = [];
  let loading = true;
  let selectedProgram: any = null;
  let editing = false;
  let saveMsg: string | null = null;
  let errorMsg = '';
  let activeTab = 'preview'; // 'preview' or 'raw'
  let jsonContent: any = {};
  let editingProgram: any = null;
  let addingProgram = false;

  // 동적 트리 구조 데이터 (자유로운 깊이)
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

  // 새 프로그램 폼
  let newProgram = {
    name: '',
    description: '',
    created_at: new Date().toISOString().split('T')[0]
  };

  /* 초기 데이터 로드 */
  onMount(async () => {
    try {
      loading = true;
      const rawPrograms = await fetchPrograms();
      // uid를 id로 매핑
      programs = rawPrograms.map((program: any) => ({
        ...program,
        id: program.uid || program.id
      }));
      console.log('Fetched programs:', programs); // 디버깅용
    } catch (e: any) {
      errorMsg = e.message ?? '프로그램 로드 실패';
      programs = [];
    } finally {
      loading = false;
    }
  });

  /* 자유로운 트리 구조 관리 */
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
      // 최상위 노드인 경우 treeData.nodes에서 해당 노드를 찾아서 업데이트
      const nodeIndex = treeData.nodes.findIndex((n: any) => n.id === node.id);
      if (nodeIndex !== -1) {
        treeData.nodes[nodeIndex] = { ...node };
      }
    }
    treeData = { ...treeData };
    jsonContent = treeToJSON();
  }

  // 노드를 재귀적으로 찾는 함수
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

  // 새로운 통합 콜백 함수
  function handleNodeChange(node: any, changeType: string, parent: any, index: number) {
    console.log('=== handleNodeChange 호출됨 ===');
    console.log('node:', node);
    console.log('changeType:', changeType);
    console.log('parent:', parent);
    console.log('index:', index);
    
    if (changeType === 'tree' || changeType === 'spec') {
      // nodeKind 변경 (트리/스펙 전환) - 새로운 노드 객체를 받음
      console.log('트리/스펙 전환 처리 중...');
      const result = findNodeAndParent(treeData.nodes, node.id);
      console.log('findNodeAndParent 결과:', result);
      
      if (result) {
        if (result.parent) {
          console.log('하위 노드 업데이트:', result.parent.children[result.index], '->', node);
          result.parent.children[result.index] = node; // 새로운 노드 객체로 교체
        } else {
          console.log('최상위 노드 업데이트:', treeData.nodes[result.index], '->', node);
          treeData.nodes[result.index] = node; // 새로운 노드 객체로 교체
        }
        console.log('treeData 업데이트 전:', treeData);
        treeData = { ...treeData }; // 강제로 반응성 트리거
        console.log('treeData 업데이트 후:', treeData);
        jsonContent = treeToJSON(); // 명시적으로 JSON 업데이트
        console.log('jsonContent 명시적 업데이트:', jsonContent);
      } else {
        console.log('노드를 찾을 수 없음!');
      }
    } else {
      // type 변경 (라디오 버튼)
      console.log('타입 변경 처리 중...');
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

  /* 트리 데이터를 JSON으로 변환 */
  function treeToJSON() {
    console.log('treeToJSON 호출됨 - treeData:', treeData);
    
    function convertNode(node: any): any {
      console.log('convertNode 호출됨:', node);
      if (node.nodeKind === 'spec') {
        // 스펙 노드는 type만 반환 (value 제거)
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
    
    console.log('treeToJSON 결과:', result);
    return result;
  }

  /* JSON을 트리 데이터로 변환 */
  function jsonToTree(json: any) {
    function convertToNode(key: string, value: any): any {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        // 객체인 경우 tree 노드
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
        // 기본값인 경우 spec 노드
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

  // 트리 데이터가 변경될 때마다 JSON 콘텐츠 업데이트
  $: if (treeData && treeData.nodes) {
    console.log('=== Reactive Statement 1 실행됨 ===');
    console.log('treeData:', treeData);
    console.log('treeData.nodes:', treeData.nodes);
    jsonContent = treeToJSON();
    console.log('jsonContent 업데이트됨:', jsonContent);
    console.log('JSON updated from reactive:', jsonContent); // 디버깅용
  }
  
  // treeData 변경 시마다 JSON 업데이트 (추가 보장)
  $: treeData && (() => {
    console.log('=== Reactive Statement 2 실행됨 ===');
    console.log('treeData 변경 감지:', treeData);
    jsonContent = treeToJSON();
    console.log('JSON updated from treeData change:', jsonContent); // 디버깅용
  })();

  /* 프로그램 선택 */
  async function selectProgram(program: any) {
    console.log('Selected program:', program); // 디버깅용
    selectedProgram = program;
    try {
      // id가 없으면 name을 사용
      const identifier = program.id || program.name;
      const summaryFormat = await fetchSummaryFormat(identifier);
      console.log('Fetched summary format:', summaryFormat); // 디버깅용
      treeData = jsonToTree(summaryFormat);
      jsonContent = treeToJSON();
    } catch (e) {
      console.log('Error fetching summary format:', e); // 디버깅용
      treeData = { nodes: [] };
      jsonContent = {};
    }
    editing = false;
    saveMsg = '';
  }

  /* 저장 */
  async function saveProgram() {
    if (!selectedProgram) return;
    try {
      const jsonData = activeTab === 'raw' ? jsonContent : treeToJSON();
      await updateSummaryFormat(selectedProgram.id, jsonData);
      saveMsg = '저장되었습니다!';
      editing = false;
    } catch (e: any) {
      errorMsg = e.message ?? '저장 실패';
    }
  }

  /* CRUD 기능 */
  async function addProgram() {
    // 모달 상태 및 관련 변수/함수 완전히 삭제
    // <div class="fixed ...">로 시작하는 showAddModal, showEditModal, showDeleteModal 관련 UI 블록도 모두 삭제
    // 이제 추가/수정/삭제는 모두 페이지 내에서만 동작하도록 유지
  }

  async function handleAddProgram() {
    try {
      const createdProgram = await createProgram(newProgram);
      // 새 프로그램 추가 후 목록을 다시 불러옴
      programs = await fetchPrograms();
      newProgram = {
        name: '',
        description: '',
        created_at: new Date().toISOString().split('T')[0]
      };
      errorMsg = '';
    } catch (e: any) {
      errorMsg = e.message ?? '프로그램 추가 실패';
    }
  }

  function editProgram(program: any) {
    editingProgram = { ...program };
    // 트리 데이터 초기화 (program의 속성에서 변환)
    if (program.properties) {
      treeData = jsonToTree(program.properties);
    } else {
      treeData = { nodes: [] };
    }
    // jsonContent 초기화
    jsonContent = treeToJSON();
  }

  function cancelEdit() {
    editingProgram = null;
    addingProgram = false;
    treeData = { nodes: [] };
  }

  function handleAddProgramClick() {
    addingProgram = true;
    editingProgram = {
      name: '',
      description: '',
      status: 'active',
      created_at: new Date().toISOString().split('T')[0]
    };
    treeData = { nodes: [] };
    jsonContent = treeToJSON();
    saveMsg = '';
    errorMsg = '';
  }

  async function saveEdit() {
    if (!editingProgram) return;
    const propertiesData = treeToJSON();
    try {
      if (addingProgram) {
        const created = await createProgram({
          name: editingProgram.name,
          description: editingProgram.description,
          status: editingProgram.status || 'active',
          created_at: editingProgram.created_at
        });
        await updateProgram(created.id, {
          name: editingProgram.name,
          description: editingProgram.description,
          status: editingProgram.status || 'active',
          properties: propertiesData
        });
        addingProgram = false;
      } else {
        // ID가 없으면 에러 처리
        if (!editingProgram.id) {
          errorMsg = '프로그램 ID가 없습니다. 프로그램을 다시 선택해주세요.';
          return;
        }
        await updateProgram(editingProgram.id, {
          name: editingProgram.name,
          description: editingProgram.description,
          status: editingProgram.status || 'active',
          properties: propertiesData
        });
      }
      // 프로그램 목록을 다시 로드할 때도 uid를 id로 매핑
      const rawPrograms = await fetchPrograms();
      programs = rawPrograms.map((program: any) => ({
        ...program,
        id: program.uid || program.id
      }));
      toastMsg.set('저장되었습니다!');
      errorMsg = '';
      setTimeout(() => { toastMsg.set(''); }, 2000);
    } catch (e: any) {
      errorMsg = e.message ?? '저장 실패';
      toastMsg.set('');
    }
  }
  
  // treeData 변경 시 저장 메시지 자동 제거
  $: if (treeData && saveMsg) {
    saveMsg = '';
  }

  async function deleteProgramConfirm(program: any) {
    // 기존 코드 유지
  }

  async function handleDeleteProgram(programId: string) {
    try {
      await deleteProgram(programId);
      programs = await fetchPrograms();
      toastMsg.set('삭제되었습니다!');
      setTimeout(() => { toastMsg.set(''); }, 2000);
    } catch (e: any) {
      errorMsg = e.message ?? '삭제 실패';
      toastMsg.set('');
    }
  }

  /* 프로그램 수정용 동적 트리 구조 관리 */
  function addEditRequirement() {
    // 기존 코드 유지
  }

  function removeEditRequirement(index: number) {
    // 기존 코드 유지
  }

  function addEditTrial(parent: any) {
    // 기존 코드 유지
  }

  function removeEditTrial(parent: any, index: number) {
    // 기존 코드 유지
  }

  function addEditField(parent: any) {
    // 기존 코드 유지
  }

  function removeEditField(parent: any, index: number) {
    // 기존 코드 유지
  }

  /* 수정용 트리 데이터를 JSON으로 변환 */
  function editTreeToJSON() {
    // 기존 코드 유지
  }

  function onNodeNameInput(node) {
    // 트리 구조가 바뀌었으므로 미리보기 즉시 갱신
    jsonContent = treeToJSON();
  }

  $: jsonContent = treeToJSON();
</script>

{#if saveMsg}
  <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 text-green-700 bg-green-100 border border-green-300 px-6 py-2 rounded shadow">
    {saveMsg}
  </div>
{/if}

<div class="flex gap-6">
  <div class="w-2/3">
    <!-- 왼쪽: 프로그램 목록 -->
    <div class="flex gap-8 h-full">
      <div class="w-1/4">
        <h2 class="font-bold mb-2">프로그램 목록</h2>
        <div class="mb-2">
          <button class="btn btn-primary btn-sm" on:click={handleAddProgramClick}>새 프로그램 추가</button>
        </div>

        {#if errorMsg}
          <div class="text-red-600 mb-2">{errorMsg}</div>
        {/if}

        {#if loading}
          <div>Loading...</div>
        {:else}
          <div class="space-y-2 max-h-96 overflow-y-auto">
            {#each programs as program}
              <div class="p-3 border rounded cursor-pointer hover:bg-gray-50 {editingProgram?.id === program.id ? 'bg-blue-50 border-blue-300' : ''}" 
                   on:click={() => selectProgram(program)}>
                <div class="font-medium">{program.name || '이름 없음'}</div>
                <div class="text-sm text-gray-600">{program.description || '설명 없음'}</div>
                <div class="text-sm text-gray-500">{program.created_at || '날짜 없음'}</div>
                <div class="flex gap-1 mt-2">
                  <button class="btn btn-xs" on:click|stopPropagation={() => editProgram(program)}>수정</button>
                  <button class="btn btn-xs btn-error" on:click|stopPropagation={() => handleDeleteProgram(program.id)}>삭제</button>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- 중앙: 동적 트리 폼 -->
      {#if editingProgram}
        <div class="flex-1">
          <div class="flex justify-between items-center mb-4">
            <h2 class="font-bold">{addingProgram ? '프로그램 추가' : `프로그램 수정: ${editingProgram.name}`}</h2>
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
              <label class="block text-sm font-medium mb-1">프로그램명</label>
              <input type="text" bind:value={editingProgram.name} class="w-full p-2 border rounded" on:input={() => { editingProgram = { ...editingProgram }; jsonContent = treeToJSON(); }} />
            </div>
            <div class="mb-3">
              <label class="block text-sm font-medium mb-1">설명</label>
              <input type="text" bind:value={editingProgram.description} class="w-full p-2 border rounded" on:input={() => { editingProgram = { ...editingProgram }; jsonContent = treeToJSON(); }} />
            </div>
            <div class="mb-3">
              <label class="block text-sm font-medium mb-1">상태</label>
              <select bind:value={editingProgram.status} class="w-full p-2 border rounded">
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
        <div class="text-gray-500">프로그램을 선택하여 포맷을 편집하세요.</div>
      {/if}
    </div>
  </div>
  <div class="w-1/3">
    <h3 class="font-bold mb-2">JSON 미리보기</h3>
    {#if editingProgram}
      <div class="mb-2 text-xs text-gray-500">
        마지막 업데이트: {new Date().toLocaleTimeString()}
      </div>
      <pre class="bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">{JSON.stringify(jsonContent, null, 2)}</pre>
    {:else}
      <div class="text-gray-400">프로그램을 선택하여 JSON을 확인하세요.</div>
    {/if}
  </div>
</div>
 