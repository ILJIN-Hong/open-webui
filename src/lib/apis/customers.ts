const RAG_BASE_URL = 'http://192.168.141.235:9000/api/customers';

export async function fetchCustomers() {
  const res = await fetch(`${RAG_BASE_URL}/list`);
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  const data = await res.json();
  return data;
}

export async function fetchCustomer(customerId: string) {
  const res = await fetch(`${RAG_BASE_URL}/get/${customerId}`);
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  const data = await res.json();
  return data;
}

export async function createCustomer(customerData: any) {
  const res = await fetch(`${RAG_BASE_URL}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: customerData.name,
      description: customerData.description,
      created_at: customerData.created_at
    })
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  const data = await res.json();
  return data;
}

export async function updateCustomer(customerId: string, customerData: any) {
  const requestBody = {
    name: customerData.name,
    description: customerData.description,
    status: customerData.status,
    properties: customerData.properties
  };
  const res = await fetch(`${RAG_BASE_URL}/update/${customerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  const data = await res.json();
  return data;
}

export async function deleteCustomer(customerId: string) {
  const res = await fetch(`${RAG_BASE_URL}/delete/${customerId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  return { message: 'Customer deleted successfully' };
}

export async function fetchSummaryFormat(customerId: string) {
  const customer = await fetchCustomer(customerId);
  return customer.summary_format || {};
}

export async function updateSummaryFormat(customerId: string, summary: any) {
  const res = await fetch(`${RAG_BASE_URL}/summary/${customerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      summary_format: summary
    })
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  return { message: 'Summary format updated successfully' };
} 