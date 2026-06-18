@@
 import { BrowserRouter, Routes, Route } from 'react-router-dom'
+import AdminProviders from './pages/AdminProviders'
@@
               <Route path="/templates" element={<Templates/>} />
               <Route path="/templates/new" element={<TemplateEditor/>} />
+              <Route path="/admin/providers" element={<AdminProviders/>} />
               <Route path="/campaigns/new" element={<CampaignBuilder/>} />
               <Route path="/inbox" element={<Inbox/>} />
