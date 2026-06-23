/**
 * Auth route middleware.
 * Protects pages that require login (e.g., /create).
 * Redirects to /login if not authenticated.
 */
export default defineNuxtRouteMiddleware(async (to, from) => {
  const { isLoggedIn, init } = useAuth()

  // Try to restore session from localStorage token
  await init()

  if (!isLoggedIn.value) {
    return navigateTo('/login')
  }
})
