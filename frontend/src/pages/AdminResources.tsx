import React, { useState, useEffect, useCallback, FormEvent } from 'react';
import { listResources, createResource, updateResource, deleteResource } from '../api/resources';
import { Resource, ResourceCreate, ResourceUpdate } from '../types';
import Modal from '../components/Modal';

const AdminResources: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentResource, setCurrentResource] = useState<ResourceCreate | ResourceUpdate | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [modalError, setModalError] = useState('');

  const defaultResource: ResourceCreate = {
    name: '',
    type: 'room',
    capacity: 1,
    hourly_rate: 10,
    features: '{}',
    open_hour: '09:00',
    close_hour: '21:00',
  };

  const fetchResources = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listResources();
      setResources(data);
    } catch (err) {
      setError('Failed to fetch resources.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  const openCreateModal = () => {
    setCurrentResource(defaultResource);
    setEditingId(null);
    setModalError('');
    setIsModalOpen(true);
  };

  const openEditModal = (resource: Resource) => {
    // FIX: Destructure the resource to separate the `id` from the editable data.
    // The `currentResource` state is not supposed to have an `id`, which caused the type error.
    const { id, ...editableData } = resource;
    setCurrentResource(editableData);
    setEditingId(resource.id);
    setModalError('');
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setCurrentResource(null);
    setEditingId(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    if (currentResource) {
      setCurrentResource({
        ...currentResource,
        [name]: ['capacity', 'hourly_rate'].includes(name) ? Number(value) : value,
      });
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!currentResource) return;

    // Validate features JSON
    try {
        if (currentResource.features) {
            JSON.parse(currentResource.features);
        }
    } catch {
        setModalError("Features must be a valid JSON object.");
        return;
    }

    try {
      if (editingId) {
        await updateResource(editingId, currentResource as ResourceUpdate);
      } else {
        await createResource(currentResource as ResourceCreate);
      }
      closeModal();
      fetchResources(); // Refresh list
    } catch (err: any) {
      setModalError(err.response?.data?.detail || 'An error occurred.');
    }
  };
  
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this resource? This action cannot be undone.')) {
        try {
            await deleteResource(id);
            fetchResources(); // Refresh list
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete resource.');
        }
    }
  };

  if (loading) return <div>Loading resources...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="container mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Manage Resources</h1>
        <button onClick={openCreateModal} className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">
          Create New Resource
        </button>
      </div>
      
      <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th className="p-4">Name</th>
              <th className="p-4">Type</th>
              <th className="p-4">Capacity</th>
              <th className="p-4">Rate/hr</th>
              <th className="p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {resources.map((resource) => (
              <tr key={resource.id} className="border-b dark:border-gray-700">
                <td className="p-4">{resource.name}</td>
                <td className="p-4 capitalize">{resource.type}</td>
                <td className="p-4">{resource.capacity}</td>
                <td className="p-4">${resource.hourly_rate.toFixed(2)}</td>
                <td className="p-4 space-x-2">
                  <button onClick={() => openEditModal(resource)} className="text-indigo-600 hover:underline">Edit</button>
                  <button onClick={() => handleDelete(resource.id)} className="text-red-600 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal isOpen={isModalOpen} onClose={closeModal} title={editingId ? 'Edit Resource' : 'Create Resource'}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {modalError && <p className="text-red-500">{modalError}</p>}
          <InputField name="name" label="Name" value={currentResource?.name || ''} onChange={handleChange} required />
          <div>
              <label htmlFor="type" className="block text-sm font-medium mb-1">Type</label>
              <select name="type" id="type" value={currentResource?.type} onChange={handleChange} className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600">
                  <option value="room">Room</option>
                  <option value="seat">Seat</option>
                  <option value="equipment">Equipment</option>
              </select>
          </div>
          <InputField name="capacity" label="Capacity" type="number" value={currentResource?.capacity || 1} onChange={handleChange} required min={1} />
          <InputField name="hourly_rate" label="Hourly Rate ($)" type="number" value={currentResource?.hourly_rate || 0} onChange={handleChange} required min={0} step={0.01} />
          <InputField name="open_hour" label="Opening Hour (HH:MM)" value={currentResource?.open_hour || ''} onChange={handleChange} placeholder="09:00" />
          <InputField name="close_hour" label="Closing Hour (HH:MM)" value={currentResource?.close_hour || ''} onChange={handleChange} placeholder="21:00" />
          <div>
            <label htmlFor="features" className="block text-sm font-medium mb-1">Features (JSON format)</label>
            <textarea name="features" id="features" value={currentResource?.features || ''} onChange={handleChange} rows={3} className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600 font-mono text-sm" placeholder='{"whiteboard": true, "outlets": 4}' />
          </div>
          <div className="flex justify-end space-x-2 pt-2">
            <button type="button" onClick={closeModal} className="bg-gray-200 dark:bg-gray-600 py-2 px-4 rounded hover:bg-gray-300 dark:hover:bg-gray-500">Cancel</button>
            <button type="submit" className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700">Save Resource</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

// Helper component for form fields
const InputField: React.FC<{name: string, label: string, value: string | number, onChange: any, type?: string, required?: boolean, min?: number, step?: number, placeholder?: string}> = ({ name, label, ...props }) => (
    <div>
        <label htmlFor={name} className="block text-sm font-medium mb-1">{label}</label>
        <input id={name} name={name} {...props} className="w-full p-2 border rounded bg-gray-50 dark:bg-gray-700 border-gray-300 dark:border-gray-600" />
    </div>
);


export default AdminResources;