<script lang="ts">
	import example_img from '$lib/assets/example.jpg';

	const { onButtonClick, description, buttonText, buttonEnabled } = $props();
</script>

<div class="relative h-screen w-64 bg-gray-600 px-2 text-white">
	<h1 class="pt-2 pb-1 text-center text-4xl font-bold">Draw2Route</h1>

	<p>
		Want to spice your run up? Have a cool strava profile? Draw a shape and we'll try to draw it
		using streets!
		<br />
		<span class="text-xs font-extralight italic"
			>(Accurcy may vary based on location and street availability)</span
		>
	</p>

	<img
		src={example_img}
		alt="Example route drawn on a map"
		class="my-4 rounded border border-white"
	/>

	<hr class="my-2 border-white" />

	<p>
		{description}
	</p>
	{#if buttonText != ''}
		<div class="absolute bottom-4 left-0 w-full px-3">
			<button
				class="w-full rounded bg-blue-500 px-4 py-2 text-white hover:cursor-pointer hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-gray-400"
				onclick={onButtonClick}
				disabled={!buttonEnabled}
			>
				{buttonText}
			</button>
		</div>
	{/if}
</div>
