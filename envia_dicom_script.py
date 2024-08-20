import os
import concurrent.futures
import pydicom
from pynetdicom import AE, sop_class

def export_exam(file_path):
    try:
        # Carregar o arquivo DICOM usando pydicom
        dicom_dataset = pydicom.dcmread(file_path)

        # Configurar a associação DICOM
        ae = AE(ae_title=b'DWS')
        ae.add_requested_context(sop_class.StudyRootQueryRetrieveInformationModelFind)
        ae.add_requested_context(sop_class.StudyRootQueryRetrieveInformationModelMove)
        ae.add_requested_context(sop_class.PatientRootQueryRetrieveInformationModelFind)
        ae.add_requested_context(sop_class.PatientRootQueryRetrieveInformationModelMove)

        # Adicionar contexto de apresentação para 'Ultrasound Image Storage'
        ae.add_requested_context(sop_class.UltrasoundImageStorage, transfer_syntax=pydicom.uid.JPEGLossless)

        # Adicionar contextos para outras modalidades DICOM
        modalities = ['CT', 'CR', 'MR', 'DX']
        for modality in modalities:
            uid = getattr(sop_class, f'{modality}ImageStorage', None)
            if uid:
                ae.add_requested_context(uid, transfer_syntax=pydicom.uid.ExplicitVRLittleEndian)

        print(f"Tentando estabelecer a associação DICOM para o arquivo: {file_path}")

        # Estabelecer a associação DICOM
        assoc = ae.associate('192.168.1.124', 4200, ae_title=b'PIXCEDILEME')

        if assoc.is_established:
            # Construir o conjunto de dados DICOM para a exportação
            export_dataset = dicom_dataset

            # Enviar o conjunto de dados DICOM sem o argumento message_id
            status, _ = assoc.send_c_store(export_dataset)

            # Verificar o status da exportação
            if status:
                print(f"Exportação do arquivo {file_path} concluída com sucesso.")
            else:
                print(f"Falha ao exportar o arquivo {file_path}.")

            # Encerrar a associação DICOM
            assoc.release()
        else:
            print(f"Falha ao estabelecer a associação DICOM para o arquivo {file_path}.")

    except Exception as e:
        print(f"Erro inesperado ao processar o arquivo {file_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    root_directory = input("Digite o caminho do diretório de origem: ")

    if not os.path.exists(root_directory):
        print(f"O diretório '{root_directory}' não existe. Saindo do programa.")
        return

    files = [os.path.join(root, file) for root, dirs, files in os.walk(root_directory) for file in files if file.endswith('.dcm')]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(export_exam, files)

if __name__ == "__main__":
    main()