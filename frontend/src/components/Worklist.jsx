import React, { useState } from 'react';
import { Clock, AlertCircle, CheckCircle, ChevronRight, FileText } from 'lucide-react';
import clsx from 'clsx';
import worklistData from '../mock/worklist.json';
import { Card } from './ui/Card';
import { DataBadge } from './ui/DataBadge';

export default function Worklist({ onSelectScan }) {
  const [selectedRow, setSelectedRow] = useState(null);
  
  const getUrgencyIcon = (urgency) => {
    const icons = {
      high: <AlertCircle className="w-4 h-4 text-diagnostic-critical" />,
      medium: <Clock className="w-4 h-4 text-diagnostic-warning" />,
      low: <CheckCircle className="w-4 h-4 text-diagnostic-normal" />,
    };
    return icons[urgency] || icons.low;
  };
  
  const getBadgeStatus = (urgency) => {
      switch(urgency) {
          case 'high': return 'critical';
          case 'medium': return 'warning';
          default: return 'normal';
      }
  };

  const handleRowClick = (item) => {
      setSelectedRow(item.id);
      if (onSelectScan) {
          onSelectScan(item);
      }
  };
  
  return (
    <Card variant="default" className="overflow-hidden p-0 border border-white/10 shadow-clinical-lg">
      <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
        <div>
            <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-medical-primary" />
                Diagnostic Worklist
            </h3>
            <p className="text-sm text-clinical-400 mt-1">Recent scans requiring review</p>
        </div>
        <div className="flex gap-2">
            <span className="px-3 py-1 rounded-full bg-white/5 text-xs text-clinical-300 font-medium">
                {worklistData.length} Pending
            </span>
        </div>
      </div>

      <div className="overflow-x-auto clinical-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead className="bg-white/[0.03] text-clinical-400 text-xs uppercase tracking-wider font-semibold">
            <tr>
              <th className="px-6 py-4 border-b border-white/5">Patient ID</th>
              <th className="px-6 py-4 border-b border-white/5">Scan Time</th>
              <th className="px-6 py-4 border-b border-white/5">AI Diagnosis</th>
              <th className="px-6 py-4 border-b border-white/5">Confidence</th>
              <th className="px-6 py-4 border-b border-white/5">Urgency</th>
              <th className="px-6 py-4 border-b border-white/5 w-10"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {worklistData.map((item) => (
              <tr 
                key={item.id}
                onClick={() => handleRowClick(item)}
                className={clsx(
                  'cursor-pointer transition-all duration-200 group hover:bg-white/[0.04]',
                  selectedRow === item.id ? 'bg-medical-primary/10 border-l-2 border-medical-primary' : 'border-l-2 border-transparent'
                )}
              >
                <td className="px-6 py-4 font-mono text-sm text-clinical-100 font-medium group-hover:text-white transition-colors">
                    {item.patientId}
                </td>
                <td className="px-6 py-4 text-sm text-clinical-300">
                    {item.scanDate}
                </td>
                <td className="px-6 py-4 text-sm font-medium text-white">
                    {item.diagnosis}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                     <div className="w-16 h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div 
                            className="h-full bg-medical-accent rounded-full" 
                            style={{ width: `${item.confidence * 100}%` }}
                        />
                     </div>
                     <span className="text-xs font-bold text-medical-accent">{(item.confidence * 100).toFixed(0)}%</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <DataBadge 
                    status={getBadgeStatus(item.urgency)} 
                    label="" 
                    value={item.urgency.charAt(0).toUpperCase() + item.urgency.slice(1)} 
                    className="text-[10px] py-0.5 px-2 uppercase tracking-wide"
                  />
                </td>
                <td className="px-6 py-4 text-right">
                    <ChevronRight className={clsx("w-4 h-4 text-clinical-400 transition-transform", selectedRow === item.id ? "text-medical-primary translate-x-1" : "group-hover:translate-x-1")} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
