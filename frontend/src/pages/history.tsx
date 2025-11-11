/**
 * History Page
 * Validation history with search and filtering
 */

import React, { useState } from 'react'
import { Search, Filter, Download, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useHistory, useDeleteHistoryItem, useHistoryFilter } from '@/hooks/use-history'
import { formatDate, getStatusColor } from '@/lib/utils'

export function HistoryPage() {
  const [page, setPage] = useState(1)
  const pageSize = 20

  const { filter, updateFilter, resetFilter } = useHistoryFilter()
  const { data, isLoading } = useHistory(page, pageSize, filter)
  const { mutate: deleteItem } = useDeleteHistoryItem()

  const handleSearch = (query: string) => {
    updateFilter({ searchQuery: query })
    setPage(1)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Validation History</h1>
          <p className="text-muted-foreground">
            View and manage your validation history
          </p>
        </div>
        <Button variant="outline">
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search validations..."
                className="pl-9"
                value={filter.searchQuery || ''}
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>
            <Button variant="outline" onClick={resetFilter}>
              <Filter className="h-4 w-4 mr-2" />
              Reset Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* History Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Validations</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : data?.items.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No validation history found</p>
            </div>
          ) : (
            <div className="space-y-3">
              {data?.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-3">
                      <p className="font-medium">
                        {item.documentName || 'Untitled Document'}
                      </p>
                      <Badge variant={getStatusBadgeVariant(item.status)}>
                        {item.status}
                      </Badge>
                      {item.corrected && (
                        <Badge variant="success">Corrected</Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>{formatDate(item.timestamp, 'relative')}</span>
                      <span>Score: {item.score}%</span>
                      <span>{item.totalIssues} issues</span>
                      <span>{item.modules.join(', ')}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteItem(item.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {data && data.totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-muted-foreground">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, data.total)} of{' '}
                {data.total} results
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  Previous
                </Button>
                <span className="text-sm">
                  Page {page} of {data.totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page === data.totalPages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function getStatusBadgeVariant(status: string): 'success' | 'warning' | 'destructive' {
  switch (status) {
    case 'passed':
      return 'success'
    case 'warning':
      return 'warning'
    case 'failed':
      return 'destructive'
    default:
      return 'warning'
  }
}
