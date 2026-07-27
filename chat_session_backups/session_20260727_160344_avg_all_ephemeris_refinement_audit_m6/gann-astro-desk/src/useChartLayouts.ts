import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  deleteChartLayout,
  deleteDrawingTemplate,
  fetchChartLayout,
  fetchChartLayouts,
  fetchDrawingTemplates,
  recordFrontendDiagnostic,
  saveChartLayout,
  saveDrawingTemplate,
} from './api'
import {
  defaultDrawingPreferences,
  defaultRsiPaneSettings,
  layoutSignature,
  validateImportedLayout,
  type ChartLayoutScope,
} from './chartLayouts'
import { normalizeCollectiveAuditSnapshots } from './collectiveAudit'
import { migrateLegacySquareOfNineDrawing } from './squareOfNineWorkspace'
import { normalizePlanetaryLineSettings } from './planetaryLines'
import type {
  ChartDrawing,
  ChartLayout,
  ChartLayoutState,
  DrawingTemplate,
} from './types'

export type LayoutSaveStatus = 'loading' | 'saved' | 'saving' | 'conflict' | 'error'

type UseChartLayoutsOptions = {
  scope: ChartLayoutScope
  initialChartState: ChartLayoutState
  onRestoreChartState?: (state: ChartLayoutState) => void
  enabled?: boolean
}

function scopeKey(scope: ChartLayoutScope): string {
  return [scope.workspaceKind, scope.symbol, scope.timeframe, scope.familyKey].join('::')
}

function defaultLayoutName(scope: ChartLayoutScope): string {
  if (scope.workspaceKind === 'analysis') {
    const family = scope.familyKey.split('::').slice(-2).join(' ')
    return `${scope.symbol} ${scope.timeframe} ${family || 'Aspect review'}`
  }
  return `${scope.symbol} ${scope.timeframe} Default`
}

export function useChartLayouts({
  scope,
  initialChartState,
  onRestoreChartState,
  enabled = true,
}: UseChartLayoutsOptions) {
  const { workspaceKind, symbol, timeframe, familyKey } = scope
  const [layouts, setLayouts] = useState<ChartLayout[]>([])
  const [activeLayout, setActiveLayout] = useState<ChartLayout | null>(null)
  const [drawings, setDrawingState] = useState<ChartDrawing[]>([])
  const [chartState, setChartStateValue] = useState<ChartLayoutState>(initialChartState)
  const [templates, setTemplates] = useState<DrawingTemplate[]>([])
  const [selectedDrawingId, setSelectedDrawingId] = useState<string | null>(null)
  const [saveStatus, setSaveStatus] = useState<LayoutSaveStatus>('loading')
  const [error, setError] = useState<string | null>(null)
  const [undoStack, setUndoStack] = useState<ChartDrawing[][]>([])
  const activeLayoutRef = useRef<ChartLayout | null>(null)
  const drawingsRef = useRef<ChartDrawing[]>([])
  const chartStateRef = useRef<ChartLayoutState>(initialChartState)
  const lastSavedSignatureRef = useRef('')
  const hydratedRef = useRef(false)
  const savingRef = useRef(false)
  const pendingSaveRef = useRef(false)
  const restoreRef = useRef(onRestoreChartState)
  const initialStateRef = useRef(initialChartState)
  const currentScopeKey = scopeKey({ workspaceKind, symbol, timeframe, familyKey })
  const stableScope = useMemo<ChartLayoutScope>(
    () => ({ workspaceKind, symbol, timeframe, familyKey }),
    [familyKey, symbol, timeframe, workspaceKind],
  )

  useEffect(() => {
    restoreRef.current = onRestoreChartState
    initialStateRef.current = initialChartState
  }, [initialChartState, onRestoreChartState])

  const installLayout = useCallback((layout: ChartLayout) => {
    const legacySquare = layout.drawings.find((drawing) => drawing.type === 'square_of_nine')
    const drawings = layout.drawings
      .filter((drawing) => drawing.type !== 'square_of_nine')
      .map((drawing) => ({
        ...drawing,
        pane: drawing.pane === 'rsi' || drawing.pane === 'global' ? drawing.pane : 'price' as const,
      }))
    const migratedChartState = legacySquare && !layout.chartState.squareOfNine
      ? {
          ...layout.chartState,
          squareOfNine: migrateLegacySquareOfNineDrawing(
            legacySquare,
            legacySquare.anchors[0]?.price ?? 1,
          ),
        }
      : layout.chartState
    const chartState = {
      ...migratedChartState,
      drawingPreferences: {
        ...defaultDrawingPreferences(),
        ...(migratedChartState.drawingPreferences ?? {}),
      },
      rsi: {
        ...defaultRsiPaneSettings(),
        ...(migratedChartState.rsi ?? {}),
      },
      planetaryLines: normalizePlanetaryLineSettings(migratedChartState.planetaryLines),
      collectiveAuditSnapshots: normalizeCollectiveAuditSnapshots(
        migratedChartState.collectiveAuditSnapshots,
      ),
    }
    const installedLayout = { ...layout, chartState, drawings }
    activeLayoutRef.current = installedLayout
    drawingsRef.current = drawings
    chartStateRef.current = chartState
    lastSavedSignatureRef.current = layoutSignature(chartState, drawings)
    hydratedRef.current = true
    setActiveLayout(installedLayout)
    setDrawingState(drawings)
    setChartStateValue(chartState)
    setUndoStack([])
    setSelectedDrawingId(null)
    setSaveStatus('saved')
    setError(null)
    restoreRef.current?.(chartState)
  }, [])

  const loadScope = useCallback(async () => {
    const startedAt = performance.now()
    let succeeded = false
    hydratedRef.current = false
    setSaveStatus('loading')
    setError(null)
    setLayouts([])
    setDrawingState([])
    drawingsRef.current = []
    try {
      const [availableLayouts, availableTemplates] = await Promise.all([
        fetchChartLayouts(stableScope),
        fetchDrawingTemplates(),
      ])
      setTemplates(availableTemplates)
      let selected = availableLayouts.find((item) => item.isDefault) ?? availableLayouts[0]
      if (!selected) {
        selected = await saveChartLayout({
          expectedRevision: 0,
          name: defaultLayoutName(stableScope),
          ...stableScope,
          isDefault: true,
          autosave: true,
          chartState: initialStateRef.current,
          drawings: [],
        })
      }
      setLayouts(
        availableLayouts.length
          ? availableLayouts
          : [selected],
      )
      installLayout(selected)
      succeeded = true
    } catch (loadError) {
      const message = loadError instanceof Error ? loadError.message : String(loadError)
      setError(message)
      setSaveStatus('error')
    } finally {
      void recordFrontendDiagnostic('layout_restore', performance.now() - startedAt, succeeded).catch(() => undefined)
    }
  }, [installLayout, stableScope])

  useEffect(() => {
    if (!enabled) return
    void loadScope()
  }, [currentScopeKey, enabled, loadScope])

  const replaceDrawings = useCallback((next: ChartDrawing[], remember = true) => {
    if (remember) {
      const previous = drawingsRef.current
      setUndoStack((stack) => [...stack.slice(-39), previous])
    }
    drawingsRef.current = next
    setDrawingState(next)
    setSelectedDrawingId((selected) => (
      selected && next.some((item) => item.drawingId === selected) ? selected : null
    ))
  }, [])

  const updateChartState = useCallback((update: Partial<ChartLayoutState>) => {
    const next = { ...chartStateRef.current, ...update }
    if (layoutSignature(next, drawingsRef.current) === layoutSignature(chartStateRef.current, drawingsRef.current)) {
      return
    }
    chartStateRef.current = next
    setChartStateValue(next)
  }, [])

  const executeSave = useCallback(async (): Promise<boolean> => {
    const layout = activeLayoutRef.current
    if (!layout || !hydratedRef.current) return false
    if (savingRef.current) {
      pendingSaveRef.current = true
      return false
    }
    const snapshotDrawings = drawingsRef.current
    const snapshotChartState = chartStateRef.current
    const signature = layoutSignature(snapshotChartState, snapshotDrawings)
    if (signature === lastSavedSignatureRef.current) {
      setSaveStatus('saved')
      return true
    }
    savingRef.current = true
    setSaveStatus('saving')
    setError(null)
    let savedSuccessfully = false
    try {
      const saved = await saveChartLayout({
        layoutId: layout.layoutId,
        expectedRevision: layout.revision,
        name: layout.name,
        workspaceKind: layout.workspaceKind,
        symbol: layout.symbol,
        timeframe: layout.timeframe,
        familyKey: layout.familyKey,
        isDefault: layout.isDefault,
        autosave: layout.autosave,
        chartState: snapshotChartState,
        drawings: snapshotDrawings,
      })
      activeLayoutRef.current = saved
      setActiveLayout(saved)
      setLayouts((items) => items.map((item) => (
        item.layoutId === saved.layoutId ? saved : item
      )))
      lastSavedSignatureRef.current = signature
      setSaveStatus('saved')
      savedSuccessfully = true
      return true
    } catch (saveError) {
      const message = saveError instanceof Error ? saveError.message : String(saveError)
      setError(message)
      setSaveStatus(message.includes('layout revision changed') ? 'conflict' : 'error')
      return false
    } finally {
      savingRef.current = false
      const needsAnotherSave = savedSuccessfully && (
        pendingSaveRef.current
        || layoutSignature(chartStateRef.current, drawingsRef.current) !== lastSavedSignatureRef.current
      )
      pendingSaveRef.current = false
      if (needsAnotherSave) window.setTimeout(() => void executeSave(), 0)
    }
  }, [])

  useEffect(() => {
    if (!hydratedRef.current || !activeLayout?.autosave) return
    const signature = layoutSignature(chartState, drawings)
    if (signature === lastSavedSignatureRef.current) return
    const timer = window.setTimeout(() => void executeSave(), 700)
    return () => window.clearTimeout(timer)
  }, [activeLayout?.autosave, activeLayout?.layoutId, chartState, drawings, executeSave])

  const switchLayout = useCallback(async (layoutId: string) => {
    if (layoutId === activeLayoutRef.current?.layoutId) return
    const startedAt = performance.now()
    let succeeded = false
    await executeSave()
    setSaveStatus('loading')
    try {
      installLayout(await fetchChartLayout(layoutId))
      succeeded = true
    } catch (switchError) {
      setError(switchError instanceof Error ? switchError.message : String(switchError))
      setSaveStatus('error')
    } finally {
      void recordFrontendDiagnostic('layout_restore', performance.now() - startedAt, succeeded).catch(() => undefined)
    }
  }, [executeSave, installLayout])

  const saveAs = useCallback(async (name: string): Promise<boolean> => {
    const trimmed = name.trim()
    if (!trimmed) return false
    setSaveStatus('saving')
    try {
      const saved = await saveChartLayout({
        expectedRevision: 0,
        name: trimmed,
        ...stableScope,
        isDefault: false,
        autosave: true,
        chartState: chartStateRef.current,
        drawings: drawingsRef.current.map((drawing) => ({
          ...drawing,
          drawingId: crypto.randomUUID(),
        })),
      })
      setLayouts((items) => [saved, ...items])
      installLayout(saved)
      return true
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : String(saveError))
      setSaveStatus('error')
      return false
    }
  }, [installLayout, stableScope])

  const removeLayout = useCallback(async (layoutId: string) => {
    await deleteChartLayout(layoutId)
    if (layoutId === activeLayoutRef.current?.layoutId) {
      await loadScope()
    } else {
      setLayouts((items) => items.filter((item) => item.layoutId !== layoutId))
    }
  }, [loadScope])

  const importLayout = useCallback(async (contents: string): Promise<boolean> => {
    try {
      const imported = validateImportedLayout(JSON.parse(contents) as unknown)
      const saved = await saveChartLayout({
        expectedRevision: 0,
        name: `${imported.name} (Imported)`,
        ...stableScope,
        isDefault: false,
        autosave: true,
        chartState: imported.chartState,
        drawings: imported.drawings.map((drawing) => ({
          ...drawing,
          drawingId: crypto.randomUUID(),
        })),
      })
      setLayouts((items) => [saved, ...items])
      installLayout(saved)
      return true
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : String(importError))
      setSaveStatus('error')
      return false
    }
  }, [installLayout, stableScope])

  const updateDrawing = useCallback((drawingId: string, update: Partial<ChartDrawing>) => {
    replaceDrawings(drawingsRef.current.map((drawing) => drawing.drawingId === drawingId
      ? { ...drawing, ...update, guardrails: drawing.guardrails }
      : drawing))
  }, [replaceDrawings])

  const deleteDrawing = useCallback((drawingId: string) => {
    replaceDrawings(drawingsRef.current.filter((drawing) => drawing.drawingId !== drawingId))
  }, [replaceDrawings])

  const updateDrawingGroup = useCallback((
    groupId: string,
    update: Partial<Pick<ChartDrawing, 'visible' | 'locked' | 'groupName' | 'syncScope'>>,
  ) => {
    replaceDrawings(drawingsRef.current.map((drawing) => drawing.groupId === groupId
      ? { ...drawing, ...update, guardrails: drawing.guardrails }
      : drawing))
  }, [replaceDrawings])

  const deleteDrawingGroup = useCallback((groupId: string) => {
    replaceDrawings(drawingsRef.current.filter((drawing) => (
      drawing.groupId !== groupId || drawing.locked
    )))
  }, [replaceDrawings])

  const undo = useCallback(() => {
    setUndoStack((stack) => {
      const previous = stack.at(-1)
      if (!previous) return stack
      drawingsRef.current = previous
      setDrawingState(previous)
      setSelectedDrawingId(null)
      return stack.slice(0, -1)
    })
  }, [])

  const createTemplate = useCallback(async (name: string, drawing: ChartDrawing) => {
    const saved = await saveDrawingTemplate({
      name,
      drawingType: drawing.type,
      style: drawing.style,
      settings: drawing.settings,
    })
    setTemplates((items) => [...items.filter((item) => item.templateId !== saved.templateId), saved])
    return saved
  }, [])

  const removeTemplate = useCallback(async (templateId: string) => {
    await deleteDrawingTemplate(templateId)
    setTemplates((items) => items.filter((item) => item.templateId !== templateId))
  }, [])

  return {
    layouts,
    activeLayout,
    drawings,
    chartState,
    templates,
    selectedDrawingId,
    saveStatus,
    error,
    canUndo: undoStack.length > 0,
    setSelectedDrawingId,
    replaceDrawings,
    updateChartState,
    updateDrawing,
    updateDrawingGroup,
    deleteDrawingGroup,
    deleteDrawing,
    undo,
    clearDrawings: () => replaceDrawings(drawingsRef.current.filter((drawing) => drawing.locked)),
    saveNow: executeSave,
    saveAs,
    switchLayout,
    removeLayout,
    importLayout,
    createTemplate,
    removeTemplate,
  }
}
