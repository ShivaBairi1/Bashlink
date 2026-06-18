@@
   return (
     <div className="bg-white p-6 rounded shadow">
       <div className="flex justify-between items-center">
         <h2 className="text-lg font-semibold">Dead Letter Queue</h2>
-        <button onClick={clearAll} className="px-3 py-1 bg-red-600 text-white rounded">Clear All</button>
+        <div>
+          <button onClick={clearAll} className="px-3 py-1 bg-red-600 text-white rounded mr-2">Clear All</button>
+          <button onClick={()=>batchRetry()} className="px-3 py-1 bg-green-600 text-white rounded">Retry All</button>
+        </div>
       </div>
@@
-            <div className="mt-2">
-              <button onClick={()=>retry(i.id)} className="px-3 py-1 bg-yellow-500 text-white rounded">Retry</button>
-            </div>
+            <div className="mt-2 flex space-x-2">
+              <button onClick={()=>retry(i.id)} className="px-3 py-1 bg-yellow-500 text-white rounded">Retry</button>
+              <div className="text-sm text-gray-500">Created: {new Date(i.created_at).toLocaleString()}</div>
+            </div>
           </div>
         ))}
       </div>
     </div>
   )
 }
+
+async function batchRetry(){
+  try{
+    const ids = items.map(i=>i.id)
+    await api.post('/admin/dlq/batch_retry', ids)
+    alert('Batch retry enqueued')
+  }catch(e){ alert('Batch retry failed') }
+}
