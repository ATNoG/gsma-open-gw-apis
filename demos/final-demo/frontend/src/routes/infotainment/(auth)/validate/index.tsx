import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/infotainment/(auth)/validate/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/(auth)/validate/"!</div>
}
