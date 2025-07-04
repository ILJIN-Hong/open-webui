<script lang="ts">
	import { getContext } from 'svelte';
	import { page } from '$app/stores';
	const i18n = getContext('i18n');

	const tabs = [
		{ href: '/rfq', label: 'RFQ List' },
		{ href: '/rfq/upload', label: 'Upload' },
		{ href: '/rfq/customers', label: 'Customer Management' },
		{ href: '/rfq/program', label: 'Program Management' },
		{ href: '/rfq/compare', label: 'Compare' }
	];
</script>

<div class="flex flex-col w-full h-full">
	<!-- Top tab bar -->
	<nav class="flex gap-1 px-6 pt-4 pb-2 border-b border-gray-200 dark:border-gray-800 bg-transparent">
		{#each tabs as tab}
			<a
				href={tab.href}
				class="min-w-fit rounded-full px-3 py-1.5 text-sm font-medium transition {($page.url.pathname === tab.href) ? 'bg-sky-100 text-sky-600 dark:bg-sky-900 dark:text-sky-200' : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'}"
			>
				{tab.label}
			</a>
		{/each}
	</nav>
	<div class="flex-1 px-6 pt-4 pb-2 overflow-y-auto">
		<slot />
	</div>
</div> 