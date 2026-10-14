import type { InjectionKey, Ref } from 'vue'
export const cartridgeControlKey: InjectionKey<Ref<boolean>> = Symbol('cartridge-insertion-lock')
