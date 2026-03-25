export type CampaignType = 'CRM' | 'CORFO';

export interface AnalysisResult {
  name: string;
  role: string;
  company: string;
  campaign: CampaignType;
  pain_point: string;
  summary: string;
  message: string;
  match_score: number;
}

export interface HistoryItem extends AnalysisResult {
  id: number;
  status: 'Sent' | 'Not Contacted';
  created_at: string;
}

export interface Stats {
  total: number;
  matches: number;
  sent: number;
}
