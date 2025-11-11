/**
 * Document Uploader Component
 * Drag-and-drop file upload with preview
 */

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn, formatFileSize } from '@/lib/utils'

interface FileUpload {
  file: File
  id: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

interface DocumentUploaderProps {
  onFileSelect: (content: string, fileName: string) => void
  accept?: Record<string, string[]>
  maxSize?: number
  multiple?: boolean
}

export function DocumentUploader({
  onFileSelect,
  accept = {
    'text/plain': ['.txt'],
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  },
  maxSize = 10 * 1024 * 1024, // 10MB
  multiple = false,
}: DocumentUploaderProps) {
  const [files, setFiles] = useState<FileUpload[]>([])

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles: FileUpload[] = acceptedFiles.map((file) => ({
        file,
        id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
        status: 'pending',
        progress: 0,
      }))

      setFiles((prev) => (multiple ? [...prev, ...newFiles] : newFiles))

      // Process files
      newFiles.forEach(async (fileUpload) => {
        try {
          updateFileStatus(fileUpload.id, 'uploading', 50)

          const content = await readFileContent(fileUpload.file)

          updateFileStatus(fileUpload.id, 'uploading', 100)

          setTimeout(() => {
            updateFileStatus(fileUpload.id, 'success', 100)
            onFileSelect(content, fileUpload.file.name)
          }, 500)
        } catch (error) {
          updateFileStatus(
            fileUpload.id,
            'error',
            0,
            error instanceof Error ? error.message : 'Failed to read file'
          )
        }
      })
    },
    [multiple, onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
  })

  const readFileContent = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        resolve(content)
      }
      reader.onerror = () => reject(new Error('Failed to read file'))
      reader.readAsText(file)
    })
  }

  const updateFileStatus = (
    id: string,
    status: FileUpload['status'],
    progress: number,
    error?: string
  ) => {
    setFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, status, progress, error } : f))
    )
  }

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-0">
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
              isDragActive
                ? 'border-primary bg-primary/5'
                : 'border-muted-foreground/25 hover:border-primary/50',
              fileRejections.length > 0 && 'border-destructive bg-destructive/5'
            )}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            {isDragActive ? (
              <p className="text-lg font-medium">Drop files here...</p>
            ) : (
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  Drag and drop your documents here, or click to browse
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports TXT, PDF, DOC, DOCX (max {formatFileSize(maxSize)})
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {fileRejections.length > 0 && (
        <div className="rounded-lg bg-destructive/10 p-4">
          <p className="text-sm font-medium text-destructive">File upload errors:</p>
          <ul className="mt-2 space-y-1 text-sm text-destructive/80">
            {fileRejections.map(({ file, errors }) => (
              <li key={file.name}>
                {file.name}: {errors.map((e) => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((fileUpload) => (
            <Card key={fileUpload.id}>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <File className="h-8 w-8 text-muted-foreground flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{fileUpload.file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(fileUpload.file.size)}
                    </p>
                    {fileUpload.status === 'uploading' && (
                      <Progress value={fileUpload.progress} className="mt-2 h-1" />
                    )}
                    {fileUpload.status === 'error' && (
                      <p className="text-xs text-destructive mt-1">{fileUpload.error}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {fileUpload.status === 'success' && (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    )}
                    {fileUpload.status === 'error' && (
                      <AlertCircle className="h-5 w-5 text-destructive" />
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(fileUpload.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
