// Read-only definition only. No invocation or mutation.
async function sampleQspiDiagnosticBaseline(eda) {
 const sorted=(xs,key)=>[...xs].sort((a,b)=>String(a[key]).localeCompare(String(b[key])));
 const line=p=>({id:p.getState_PrimitiveId(),net:p.getState_Net(),layer:p.getState_Layer(),start:[p.getState_StartX(),p.getState_StartY()],end:[p.getState_EndX(),p.getState_EndY()],width:p.getState_LineWidth()});
 const via=p=>({id:p.getState_PrimitiveId(),net:p.getState_Net(),x:p.getState_X(),y:p.getState_Y(),diameter:p.getState_Diameter(),holeDiameter:p.getState_HoleDiameter(),viaType:p.getState_ViaType()});
 async function snapshot(){const components=[];for(const c of await eda.pcb_PrimitiveComponent.getAll()){const id=c.getState_PrimitiveId();components.push({ref:c.getState_Designator(),id,x:c.getState_X(),y:c.getState_Y(),rotation:c.getState_Rotation(),layer:c.getState_Layer(),pins:sorted(await eda.pcb_PrimitiveComponent.getAllPinsByPrimitiveId(id),'primitiveId')})}return{components:sorted(components,'id'),lines:sorted((await eda.pcb_PrimitiveLine.getAll()).map(line),'id'),vias:sorted((await eda.pcb_PrimitiveVia.getAll()).map(via),'id'),pairs:await eda.pcb_Drc.getAllDifferentialPairs(),nets:(await eda.pcb_Net.getAllNetsName()).sort(),config:await eda.pcb_Drc.getCurrentRuleConfiguration(),netRules:await eda.pcb_Drc.getNetRules(),classes:await eda.pcb_Drc.getAllNetClasses(),regionRules:await eda.pcb_Drc.getRegionRules()}}
 const document=await eda.dmt_SelectControl.getCurrentDocumentInfo(),project=await eda.dmt_Project.getCurrentProjectInfo(),state=await snapshot(),source=await eda.sys_FileManager.getDocumentSource();
 return {document,project,state,source};
}


(async()=>{const r=await sampleQspiDiagnosticBaseline(eda);if(r.document.uuid!=="7eb5cdbfc8501f0f")throw Error("wrong board");await eda.sys_FileSystem.saveFile(new Blob([JSON.stringify(r,null,2)],{type:"application/json"}),"clean_upload_core_readonly.json");})();
