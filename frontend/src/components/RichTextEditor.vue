<template>
  <div class="rich-editor" :class="{ focused: editor?.isFocused }">
    <div v-if="editor" class="editor-toolbar">
      <div class="toolbar-group">
        <button type="button" title="正文" :class="{ active: editor.isActive('paragraph') }" @click="editor.chain().focus().setParagraph().run()">正文</button>
        <button type="button" title="二级标题" :class="{ active: editor.isActive('heading', { level: 2 }) }" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()">H2</button>
        <button type="button" title="三级标题" :class="{ active: editor.isActive('heading', { level: 3 }) }" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()">H3</button>
      </div>
      <div class="toolbar-group">
        <button type="button" title="粗体" :class="{ active: editor.isActive('bold') }" @click="editor.chain().focus().toggleBold().run()"><strong>B</strong></button>
        <button type="button" title="斜体" :class="{ active: editor.isActive('italic') }" @click="editor.chain().focus().toggleItalic().run()"><em>I</em></button>
        <button type="button" title="下划线" :class="{ active: editor.isActive('underline') }" @click="editor.chain().focus().toggleUnderline().run()"><u>U</u></button>
        <button type="button" title="删除线" :class="{ active: editor.isActive('strike') }" @click="editor.chain().focus().toggleStrike().run()"><s>S</s></button>
      </div>
      <div class="toolbar-group">
        <button type="button" title="无序列表" :class="{ active: editor.isActive('bulletList') }" @click="editor.chain().focus().toggleBulletList().run()">• 列表</button>
        <button type="button" title="有序列表" :class="{ active: editor.isActive('orderedList') }" @click="editor.chain().focus().toggleOrderedList().run()">1. 列表</button>
        <button type="button" title="引用" :class="{ active: editor.isActive('blockquote') }" @click="editor.chain().focus().toggleBlockquote().run()">引用</button>
      </div>
      <div class="toolbar-group compact-group">
        <button type="button" title="左对齐" :class="{ active: editor.isActive({ textAlign: 'left' }) }" @click="editor.chain().focus().setTextAlign('left').run()">左</button>
        <button type="button" title="居中" :class="{ active: editor.isActive({ textAlign: 'center' }) }" @click="editor.chain().focus().setTextAlign('center').run()">中</button>
        <button type="button" title="右对齐" :class="{ active: editor.isActive({ textAlign: 'right' }) }" @click="editor.chain().focus().setTextAlign('right').run()">右</button>
      </div>
      <div class="toolbar-group">
        <button type="button" title="添加链接" :class="{ active: editor.isActive('link') }" @click="openLinkEditor">链接</button>
        <button type="button" title="在正文当前位置插入图片" :disabled="uploading" @click="imageInput?.click()">插图</button>
        <input ref="imageInput" class="hidden-input" type="file" accept="image/*" @change="selectImage" />
      </div>
      <div class="toolbar-group toolbar-history">
        <button type="button" title="撤销" :disabled="!editor.can().undo()" @click="editor.chain().focus().undo().run()">↶</button>
        <button type="button" title="重做" :disabled="!editor.can().redo()" @click="editor.chain().focus().redo().run()">↷</button>
      </div>
    </div>

    <div v-if="linkEditing" class="link-editor">
      <input v-model="linkUrl" type="url" placeholder="https://" @keyup.enter="applyLink" />
      <button type="button" @click="applyLink">应用</button>
      <button v-if="editor?.isActive('link')" type="button" @click="removeLink">移除</button>
      <button type="button" @click="linkEditing = false">取消</button>
    </div>

    <div v-if="uploading" class="editor-upload">
      <span>正在上传插图</span>
      <div><i :style="{ width: `${uploadProgress}%` }"></i></div>
      <strong>{{ uploadProgress }}%</strong>
    </div>

    <EditorContent :editor="editor" class="editor-content" />
    <footer class="editor-footer"><span>{{ characterCount }} 字</span></footer>
  </div>
</template>

<script setup lang="ts">
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = withDefaults(defineProps<{ modelValue: string; uploading?: boolean; uploadProgress?: number; placeholder?: string }>(), {
  uploading: false,
  uploadProgress: 0,
  placeholder: '开始撰写正文…',
})
const emit = defineEmits<{ 'update:modelValue': [value: string]; imageSelected: [file: File] }>()
const imageInput = ref<HTMLInputElement | null>(null)
const linkEditing = ref(false)
const linkUrl = ref('')

const editor = useEditor({
  content: props.modelValue || '',
  extensions: [
    StarterKit.configure({ link: { openOnClick: false, autolink: true } }),
    Underline,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Image.configure({ allowBase64: false, HTMLAttributes: { loading: 'lazy' } }),
    Placeholder.configure({ placeholder: props.placeholder }),
  ],
  editorProps: {
    attributes: { class: 'news-prose', spellcheck: 'true' },
  },
  onUpdate: ({ editor: currentEditor }) => emit('update:modelValue', currentEditor.getHTML()),
})

const characterCount = computed(() => editor.value?.getText().replace(/\s+/g, '').length || 0)

watch(() => props.modelValue, (value) => {
  if (!editor.value || value === editor.value.getHTML()) return
  editor.value.commands.setContent(value || '', { emitUpdate: false })
})

function openLinkEditor() {
  linkUrl.value = editor.value?.getAttributes('link').href || ''
  linkEditing.value = true
}

function applyLink() {
  const href = linkUrl.value.trim()
  if (!editor.value || !href) return
  editor.value.chain().focus().extendMarkRange('link').setLink({ href }).run()
  linkEditing.value = false
}

function removeLink() {
  editor.value?.chain().focus().extendMarkRange('link').unsetLink().run()
  linkEditing.value = false
}

function selectImage(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) emit('imageSelected', file)
  input.value = ''
}

function insertImage(src: string, alt = '') {
  editor.value?.chain().focus().setImage({ src, alt }).createParagraphNear().run()
}

defineExpose({ insertImage })
onBeforeUnmount(() => editor.value?.destroy())
</script>

<style scoped>
.rich-editor { overflow: hidden; border: 1px solid #d9e0dc; border-radius: 8px; background: #fff; transition: border-color .18s ease, box-shadow .18s ease; }
.rich-editor.focused { border-color: rgba(0, 135, 60, .48); box-shadow: 0 0 0 3px rgba(0, 135, 60, .08); }
.editor-toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; border-bottom: 1px solid #e5e7eb; padding: 8px 10px; background: #f8faf9; }
.toolbar-group { display: flex; align-items: center; gap: 2px; border-right: 1px solid #dde4df; padding-right: 6px; }
.toolbar-group:last-child { border-right: 0; padding-right: 0; }
.toolbar-history { margin-left: auto; }
.editor-toolbar button { display: inline-grid; place-items: center; min-width: 30px; height: 30px; border: 1px solid transparent; border-radius: 5px; padding: 0 7px; background: transparent; color: #3f4742; cursor: pointer; font-size: 12px; }
.editor-toolbar button:hover { border-color: #ccd8d0; background: #fff; color: #00873c; }
.editor-toolbar button.active { border-color: rgba(0, 135, 60, .18); background: #eaf5ee; color: #006c31; }
.editor-toolbar button:disabled { cursor: not-allowed; opacity: .38; }
.hidden-input { display: none; }
.link-editor { display: grid; grid-template-columns: minmax(180px, 1fr) auto auto auto; gap: 6px; border-bottom: 1px solid #e5e7eb; padding: 8px 10px; background: #fff; }
.link-editor input { min-width: 0; height: 32px; border: 1px solid #d7ded9; border-radius: 5px; padding: 0 9px; outline: none; }
.link-editor input:focus { border-color: #00873c; }
.link-editor button { border: 1px solid #cbd8d0; border-radius: 5px; padding: 0 10px; background: #fff; color: #1f5938; cursor: pointer; }
.editor-upload { display: grid; grid-template-columns: auto minmax(100px, 1fr) auto; align-items: center; gap: 10px; border-bottom: 1px solid #dfe7e2; padding: 8px 12px; background: #f2f8f4; color: #496056; font-size: 12px; }
.editor-upload div { overflow: hidden; height: 4px; border-radius: 2px; background: #dce8e0; }
.editor-upload i { display: block; height: 100%; background: #00873c; transition: width .15s linear; }
.editor-upload strong { color: #006c31; font-variant-numeric: tabular-nums; }
.editor-content { min-height: 430px; }
.editor-content :deep(.tiptap) { min-height: 430px; padding: 28px 34px 42px; color: #2f3437; outline: none; font-size: 16px; line-height: 1.85; }
.editor-content :deep(.tiptap p) { margin: 0 0 16px; }
.editor-content :deep(.tiptap h2) { margin: 30px 0 14px; color: #1f3d2b; font-size: 25px; line-height: 1.4; }
.editor-content :deep(.tiptap h3) { margin: 24px 0 12px; color: #1f3d2b; font-size: 20px; line-height: 1.45; }
.editor-content :deep(.tiptap ul), .editor-content :deep(.tiptap ol) { margin: 0 0 18px; padding-left: 1.6em; }
.editor-content :deep(.tiptap blockquote) { margin: 22px 0; border-left: 3px solid #00873c; padding: 3px 0 3px 18px; color: #52615a; }
.editor-content :deep(.tiptap a) { color: #007b38; text-decoration: underline; }
.editor-content :deep(.tiptap img) { display: block; max-width: min(100%, 860px); height: auto; margin: 24px auto; border-radius: 6px; }
.editor-content :deep(.tiptap p.is-editor-empty:first-child::before) { height: 0; float: left; color: #9aa39e; content: attr(data-placeholder); pointer-events: none; }
.editor-footer { display: flex; justify-content: flex-end; border-top: 1px solid #edf0ee; padding: 6px 11px; color: #87908b; font-size: 12px; }
@media (max-width: 720px) {
  .toolbar-history { margin-left: 0; }
  .link-editor { grid-template-columns: 1fr auto; }
  .editor-content, .editor-content :deep(.tiptap) { min-height: 360px; }
  .editor-content :deep(.tiptap) { padding: 20px 18px 32px; }
}
</style>
