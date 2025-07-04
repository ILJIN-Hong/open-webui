<script lang="ts">
  import RecursiveTreeNode from './RecursiveTreeNode.svelte';
  export let node: any;
  export let parent: any = null;
  export let onAdd: (parent: any) => void;
  export let onRemove: (parent: any, index: number) => void;
  export let onTypeChange: (node: any, type: string) => void;
  export let index: number;
  export let onNodeNameInput: ((node: any) => void) | undefined = undefined;

  const specTypes = [
    { value: 'number', label: '숫자' },
    { value: 'string', label: '문자열' },
    { value: 'link', label: '링크' },
    { value: 'custom', label: '사용자 정의' }
  ];
  if (!node.nodeKind) node.nodeKind = 'tree'; // 'tree' or 'spec'
  if (!node.type) node.type = 'string';

  function toggleNodeKind(node: any) {
    let newNode;
    if (node.nodeKind === 'tree') {
      // 트리 → 스펙
      newNode = {
        ...node,
        nodeKind: 'spec',
        type: 'string',
        children: undefined
      };
    } else {
      // 스펙 → 트리
      newNode = {
        ...node,
        nodeKind: 'tree',
        type: undefined,
        children: []
      };
    }
    // 상위로 새로운 노드 객체 전달
    onTypeChange(newNode, newNode.nodeKind);
  }
  
  function handleRadioChange(node: any, type: string) {
    // 라디오 버튼 변경 시에는 타입만 변경, nodeKind는 변경하지 않음
    node.type = type;
    onTypeChange(node, type);
  }
</script>

<div class="border rounded p-2 mb-2 min-w-[320px]">
  <div class="flex gap-2 mb-2 items-center">
    <input type="text" bind:value={node.name} placeholder="노드 이름" class="flex-1 p-1 border rounded min-w-[120px]" on:input={onNodeNameInput && (() => onNodeNameInput(node))} />
    <button class="btn btn-xs" on:click={() => toggleNodeKind(node)} title={node.nodeKind === 'tree' ? '스펙으로 전환' : '트리로 전환'}>
      {#if node.nodeKind === 'tree'}🌳 트리{/if}
      {#if node.nodeKind === 'spec'}🔖 스펙{/if}
    </button>
    <button class="btn btn-xs btn-error" on:click={() => onRemove(parent, index)}>삭제</button>
  </div>
  {#if node.nodeKind === 'spec'}
    <div class="ml-4 flex gap-2 items-center flex-wrap">
      {#each specTypes as t}
        <label class="flex items-center gap-1">
          <input type="radio" name={`type-${node.id}`} value={t.value} bind:group={node.type} on:change={() => handleRadioChange(node, t.value)} />
          <span>{t.label}</span>
        </label>
      {/each}
    </div>
  {:else}
    <div class="ml-4 space-y-2">
      {#each node.children ?? [] as child, childIndex}
        <RecursiveTreeNode
          node={child}
          parent={node}
          onAdd={onAdd}
          onRemove={onRemove}
          onTypeChange={onTypeChange}
          index={childIndex}
          onNodeNameInput={onNodeNameInput}
        />
      {/each}
      <button class="btn btn-xs" on:click={() => onAdd(node)}>+ 하위 노드 추가</button>
    </div>
  {/if}
</div>

<style>
  .btn-xs { font-size: 0.8rem; padding: 0.2rem 0.5rem; }
  .min-w-\[320px\] { min-width: 320px; }
  .min-w-\[120px\] { min-width: 120px; }
</style> 