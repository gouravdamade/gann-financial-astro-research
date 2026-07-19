import { ShieldCheck } from 'lucide-react'
import type { EvidenceCertification } from '../types'

type EvidenceCertificationGridProps = {
  items: EvidenceCertification[]
}

export function EvidenceCertificationGrid({ items }: EvidenceCertificationGridProps) {
  return (
    <div className="evidence-certification-grid">
      {items.map((item) => (
        <div className={`evidence-certification ${item.status}`} key={item.key} title={item.contract}>
          <header>
            <ShieldCheck size={13} />
            <strong>{item.label}</strong>
            <span>{item.badge}</span>
          </header>
          <p>{item.detail}</p>
        </div>
      ))}
    </div>
  )
}
