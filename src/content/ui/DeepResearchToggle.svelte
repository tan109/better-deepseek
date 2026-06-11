<script>
  import { onMount } from "svelte";

  let { enabled = false, onToggle = null } = $props();
  let localEnabled = $state(false);

  $effect(() => {
    localEnabled = Boolean(enabled);
  });

  onMount(() => {
    const handler = (event) => {
      localEnabled = Boolean(event.detail?.enabled);
    };
    window.addEventListener("bds:deep-research-toggle-state", handler);
    return () => window.removeEventListener("bds:deep-research-toggle-state", handler);
  });

  function handleToggle() {
    localEnabled = !localEnabled;
    if (onToggle) onToggle(localEnabled);
  }
</script>

<button
  type="button"
  class="bds-deep-research-toggle"
  class:active={localEnabled}
  onclick={handleToggle}
  aria-label={localEnabled ? "Disable Deep Research Mode" : "Enable Deep Research Mode"}
  aria-pressed={localEnabled}
  title={localEnabled ? "Deep Research Mode ON" : "Enable Deep Research Mode"}
  data-testid="deep-research-toggle"
>
  <svg
    class="bds-drt-icon"
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <circle cx="10.5" cy="10.5" r="5.5"></circle>
    <path d="m15 15 4.5 4.5"></path>
    <path d="M18 3v4"></path>
    <path d="M20 5h-4"></path>
    <path d="M5 19v2"></path>
    <path d="M6 20H4"></path>
  </svg>
  <span class="bds-drt-label">DeepResearch</span>
</button>

<style>
  :global(.bds-deep-research-mount) {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex: 0 0 auto !important;
    width: auto !important;
    height: 42px !important;
    margin-right: 8px !important;
  }

  .bds-deep-research-toggle {
    -webkit-appearance: none !important;
    appearance: none !important;
    box-sizing: border-box !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    height: 42px !important;
    min-height: 42px !important;
    max-height: 42px !important;
    margin: 0 !important;
    padding: 0 17px !important;
    border: 1px solid var(--bds-border, rgba(255, 255, 255, 0.16)) !important;
    border-radius: 999px !important;
    background: rgba(255, 255, 255, 0.02) !important;
    color: var(--bds-text-primary, #f5f7fb) !important;
    box-shadow: none !important;
    cursor: pointer !important;
    line-height: 1 !important;
    font: inherit !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    text-align: center !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    transition:
      background-color var(--bds-transition, 0.18s ease),
      border-color var(--bds-transition, 0.18s ease),
      color var(--bds-transition, 0.18s ease),
      transform 0.1s ease;
  }

  .bds-deep-research-toggle:hover {
    background-color: rgba(255, 255, 255, 0.06) !important;
    border-color: var(--bds-border-hover, rgba(255, 255, 255, 0.24)) !important;
  }

  .bds-deep-research-toggle.active {
    background-color: var(--bds-accent-glow, rgba(79, 140, 255, 0.18)) !important;
    border-color: var(--bds-accent, #4f8cff) !important;
    color: var(--bds-accent, #4f8cff) !important;
  }

  .bds-deep-research-toggle.active:hover {
    background-color: var(--bds-accent-glow, rgba(79, 140, 255, 0.22)) !important;
    border-color: var(--bds-accent, #4f8cff) !important;
  }

  .bds-deep-research-toggle:active {
    transform: scale(0.95);
  }

  .bds-drt-icon {
    width: 20px;
    height: 20px;
    flex: 0 0 auto;
    pointer-events: none;
  }

  .bds-drt-label {
    display: inline-block;
    min-width: 0;
    line-height: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
