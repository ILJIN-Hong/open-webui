const RAG_BASE_URL = 'http://192.168.141.235:9000';

export async function fetchPrograms() {
  const res = await fetch(`${RAG_BASE_URL}/api/program/list`);
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  const data = await res.json();
  
  // RAG API 서버에서 이미 programs 배열을 반환하므로 직접 사용
  return data;
}

export async function fetchProgram(programId: string) {
  const res = await fetch(`${RAG_BASE_URL}/api/program/get/${programId}`);
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  const data = await res.json();
  
  // RAG API 서버에서 직접 프로그램을 반환
  return data;
}

export async function createProgram(programData: any) {
  // RAG API 서버의 /program/add 엔드포인트 사용
  const res = await fetch(`${RAG_BASE_URL}/api/program/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: programData.name,
      description: programData.description,
      created_at: programData.created_at
    })
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  const data = await res.json();
  return data;
}

export async function updateProgram(programId: string, programData: any) {
  const requestBody = {
    name: programData.name,
    description: programData.description,
    status: programData.status,
    properties: programData.properties  // 트리 구조 데이터 포함
  };
  
  console.log('=== updateProgram API 호출 ===');
  console.log('URL:', `${RAG_BASE_URL}/api/program/update/${programId}`);
  console.log('전송 데이터:', requestBody);
  console.log('========================');
  
  const res = await fetch(`${RAG_BASE_URL}/api/program/update/${programId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  const data = await res.json();
  return data;
}

export async function deleteProgram(programId: string) {
  const res = await fetch(`${RAG_BASE_URL}/api/program/delete/${programId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  return { message: 'Program deleted successfully' };
}

export async function fetchSummaryFormat(programId: string) {
  const program = await fetchProgram(programId);
  return program.summary_format || {
    "프로그램명": "",
    "규격": "",
    "수량": 0,
    "단가": 0,
    "총액": 0,
    "납기": "",
    "비고": ""
  };
}

export async function updateSummaryFormat(programId: string, summary: any) {
  const res = await fetch(`${RAG_BASE_URL}/api/program/summary/${programId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      summary_format: summary
    })
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  return { message: 'Summary format updated successfully' };
} 