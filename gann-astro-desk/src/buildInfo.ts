const configuredCommit = import.meta.env.VITE_GANN_ASTRO_SOURCE_COMMIT

/** Present only in a reproducible desktop founder-candidate build. */
export const packagedSourceCommit = /^[0-9a-f]{40}$/i.test(configuredCommit ?? '')
  ? configuredCommit.toLowerCase()
  : null

