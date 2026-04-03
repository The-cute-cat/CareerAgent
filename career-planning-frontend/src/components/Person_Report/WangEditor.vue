
<template>
  <div class="wang-editor" :style="{ height: props.height }">
    <Toolbar
      v-if="mode === 'default'"
      style="border-bottom: 1px solid #ccc"
      :editor="editorRef"
      :defaultConfig="toolbarConfig"
      :mode="mode"
    />
    <Editor
      :style="editorStyle"
      v-model="valueHtml"
      :defaultConfig="editorConfig"
      :mode="mode"
      @onCreated="handleCreated"
      @onChange="handleChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, onBeforeUnmount, watch, computed } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import type { IDomEditor } from '@wangeditor/editor'
import '@wangeditor/editor/dist/css/style.css'

interface Props {
  modelValue: string
  height?: string
  mode?: 'default' | 'simple'
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  mode: 'default',
  placeholder: '请输入内容...'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'change': [value: string]
}>()

const editorRef = shallowRef<IDomEditor | null>(null)
const valueHtml = ref(props.modelValue)

const toolbarConfig = {
  toolbarKeys: [
    'headerSelect', '|', 'bold', 'underline', 'italic', 'color', 'bgColor', '|',
    'fontSize', '|', 'bulletedList', 'numberedList', '|',
    'justifyLeft', 'justifyCenter', 'justifyRight', '|',
    'insertLink', 'insertImage', 'insertTable', 'codeBlock', '|',
    'undo', 'redo'
  ]
}

const editorConfig = {
  placeholder: props.placeholder,
  MENU_CONF: {
    uploadImage: {
      server: '/api/upload',
      fieldName: 'file',
      maxFileSize: 5 * 1024 * 1024, // 5MB
      // 图片上传前的安全验证
      onBeforeUpload(file: File): boolean | File {
        // 验证文件类型
        const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if (!validTypes.includes(file.type)) {
          alert('仅支持 JPG、PNG、GIF、WebP 格式的图片')
          return false
        }
        return file
      },
      // 上传成功后的处理
      onSuccess(file: File, res: any) {
        console.log('Upload success:', file.name)
        return res
      },
      onFailed(file: File, res: any) {
        console.error('Upload failed:', file.name, res)
        alert('图片上传失败，请重试')
      },
      onError(file: File, err: any) {
        console.error('Upload error:', file.name, err)
        alert('图片上传出错：' + (err.message || '未知错误'))
      }
    }
  }
}

const editorStyle = computed(() => ({
  height: props.mode === 'simple' ? props.height : `calc(${props.height} - 40px)`,
  overflow: 'hidden'
}))

watch(() => props.modelValue, (val) => {
  if (val !== valueHtml.value) valueHtml.value = val
})

watch(valueHtml, (val) => emit('update:modelValue', val))

const handleCreated = (editor: IDomEditor) => {
  editorRef.value = editor
}

const handleChange = (editor: IDomEditor) => {
  emit('change', editor.getHtml())
}

onBeforeUnmount(() => {
  const editor = editorRef.value
  // 安全销毁编辑器：检查实例存在且未被销毁
  if (editor) {
    try {
      editor.destroy()
    } catch (e) {
      // 编辑器可能已被销毁或处于无效状态
      console.warn('Editor destroy warning:', e)
    }
  }
  editorRef.value = null
})
</script>

<style scoped>
.wang-editor {
  border: 1px solid #ccc;
  border-radius: 8px;
  z-index: 100;
}
</style>