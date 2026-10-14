import { ref } from 'vue'

const DARK_KEY = 'cr-theme'

function getInitial(): boolean {
  return typeof localStorage !== 'undefined' && localStorage.getItem(DARK_KEY) === 'dark'
}

const dark = ref(getInitial())

function apply() {
  document.documentElement.setAttribute('data-theme', dark.value ? 'dark' : 'light')
}
apply()

export function useTheme() {
  function toggle() {
    dark.value = !dark.value
    localStorage.setItem(DARK_KEY, dark.value ? 'dark' : 'light')
    apply()
  }
  return { dark, toggle }
}
