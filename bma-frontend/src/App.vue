<template>
  <p>Hello World</p>
  <div>
    <Button @click="toggleTheme">Simple Button</Button>

    <Button variant="warning" @click="toggleTheme">
      Warning Button
    </Button>

    <Button variant="danger" @click="toggleTheme">
      Danger Button
    </Button>

    <Button variant="disabled" @click="toggleTheme">
      Disabled Button
    </Button>

    <Button :loading="true" @click="toggleTheme">
      Loading Button
    </Button>

    <Button rounded="full" padding="lg" @click="toggleTheme">
      Rounded Full
    </Button>

    <Button bordered @click="toggleTheme">
      Bordered Button
    </Button>

    <Button margin="sm" @click="toggleTheme">
      With Margin
    </Button>

    <Button block @click="toggleTheme">
      Full Width
    </Button>

    <Button variant="danger" size="lg" rounded="lg" padding="lg" margin="sm" @click="toggleTheme">
      Delete Account
    </Button>
  </div>
  <div>
    <Input label="Username" variant="inside" />
    <Input label="Username" variant="before" />
    <Input label="Username" variant="above" />
    <Input label="Email" variant="above" width="400px" />
  </div>
  <div>
    <Card>
      Simple card content
    </Card>
    <Card>
      <template #header>
        Card Title
      </template>

      Card body content goes here.

      <template #footer>
        Footer actions
      </template>
    </Card>
  </div>
  <div>
    <Badge>Default</Badge>
    <Badge padding="10px 20px" margin="8px" variant="success">
      Spaced Badge
    </Badge>
    <Badge bordered borderColor="#000" variant="danger">
      Bordered
    </Badge>
    <Badge :rounded="false" radius="lg" variant="warning">
      Rounded Large Radius
    </Badge>
  </div>

</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import Button from './components/Button.vue'
import Input from './components/Input.vue'
import Card from './components/Card.vue'
import Badge from './components/Badge.vue'

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')

  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  }
})

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark')
  localStorage.setItem('theme', isDark ? 'dark' : 'light')
}
</script>
