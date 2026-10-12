import { createRouter, createWebHistory } from 'vue-router'
import { useSession } from '@/stores/session'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', component: () => import('@/views/TitleScreen.vue') },
    {
      path: '/hub',
      component: () => import('@/views/HubView.vue'),
      meta: { auth: true },
    },
    {
      path: '/catalog',
      component: () => import('@/views/CatalogView.vue'),
      meta: { auth: true },
    },
    {
      path: '/history',
      component: () => import('@/views/SaveHistoryView.vue'),
      meta: { auth: true },
    },
    {
      path: '/play/:gameId',
      component: () => import('@/views/CartridgeView.vue'),
      meta: { auth: true },
    },
    {
      path: '/dev/:editor?',
      component: () => import('@/views/admin/DevConsole.vue'),
      meta: { auth: true, admin: true },
    },
    { path: '/game-over', component: () => import('@/views/GameOverView.vue') },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
  scrollBehavior: () => false,
})
router.beforeEach((to) => {
  const session = useSession()
  if (to.meta.auth && !session.isLoggedIn) return '/'
  if (to.meta.admin && !session.isAdmin) return '/hub'
  if (to.path === '/' && session.isLoggedIn) return '/hub'
})
export default router
