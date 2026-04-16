import React, { useState } from 'react';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
    DialogClose
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";

interface TermsAndConditionsModalProps {
    type: 'asistente' | 'stand' | 'disertante';
    triggerText?: string;
    triggerClassName?: string;
}

export function TermsAndConditionsModal({
    type,
    triggerText = "Bases y Condiciones",
    triggerClassName = "text-blue-600 hover:text-blue-800 hover:underline text-sm font-medium transition-colors"
}: TermsAndConditionsModalProps) {
    const [open, setOpen] = useState(false);

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <button type="button" className={triggerClassName} onClick={(e) => { e.stopPropagation(); }}>
                    {triggerText}
                </button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[90vh]">
                <DialogHeader>
                    <DialogTitle className="text-xl text-center text-blue-900">
                        {type === 'asistente' && "Bases y Condiciones para Asistentes"}
                        {type === 'stand' && "Bases y Condiciones para Empresas Expositoras"}
                        {type === 'disertante' && "Bases y Condiciones para Disertantes"}
                    </DialogTitle>
                </DialogHeader>
                <ScrollArea className="h-[60vh] rounded-md border p-6 text-sm text-gray-700 bg-gray-50/50">
                    <div className="space-y-5 leading-relaxed">
                        {type === 'asistente' && <AsistenteTerms />}
                        {type === 'stand' && <StandTerms />}
                        {type === 'disertante' && <DisertanteTerms />}
                    </div>
                </ScrollArea>
                <DialogFooter className="sm:justify-end mt-4">
                    <DialogClose asChild>
                        <Button type="button" variant="default" className="w-full sm:w-auto bg-blue-900 text-white hover:bg-blue-800">
                            Cerrar y Aceptar
                        </Button>
                    </DialogClose>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}

function AsistenteTerms() {
    return (
        <>
            <p className="font-bold text-base">1. Objeto y Alcance</p>
            <p>El presente documento regula los términos y condiciones bajo los cuales los asistentes, estudiantes, docentes y profesionales (en adelante, "El Asistente") podrán inscribirse y participar en el Congreso de Logística y Transporte 2026, organizado por la Universidad Nacional Guillermo Brown (UNaB), a realizarse el día sábado 7 de noviembre de 2026.</p>

            <p className="font-bold text-base mt-4">2. Proceso de Inscripción</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La inscripción al evento es de carácter gratuito, pero de registro obligatorio y nominal.</li>
                <li>La confirmación de inscripción y el consecuente derecho de acceso (Código QR/Entrada) están sujetos a la capacidad máxima del recinto. La inscripción web no garantiza automáticamente el acceso si se supera el aforo permitido por Protección Civil el día del evento.</li>
                <li>El Asistente declara bajo juramento que los datos personales y de contacto proporcionados en el formulario de registro son verdaderos y verificables.</li>
            </ul>

            <p className="font-bold text-base mt-4">3. Inscripciones Grupales e Institucionales</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Aquellas personas que se inscriban bajo la figura de "Representante" (docentes a cargo de cursos, líderes de grupos empresariales), asumen la responsabilidad sobre la veracidad de los datos de los integrantes de su grupo y de notificar a los mismos sobre las presentes Bases y Condiciones.</li>
                <li>El Representante deberá coordinar el ingreso conjunto de su delegación en los horarios estipulados por la organización.</li>
            </ul>

            <p className="font-bold text-base mt-4">4. Normas de Convivencia y Acceso</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>El Congreso es un espacio académico y profesional. La Organización se reserva el derecho de admisión y permanencia frente a conductas que alteren el orden, falten el respeto a disertantes, expositores, personal del evento u otros asistentes.</li>
                <li>Estará prohibido el ingreso con materiales inflamables, elementos punzocortantes, alimentos y botellas de vidrio al recinto principal de conferencias.</li>
            </ul>

            <p className="font-bold text-base mt-4">5. Uso de Imagen y Datos (Ley de Protección de Datos Personales N° 25.326)</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>El Asistente autoriza expresamente e irrevocablemente a la organización del Congreso (UNaB) a captar, reproducir y difundir fotografías, videos y/o grabaciones de voz en las que pudiera aparecer durante el evento.</li>
                <li>Estas imágenes serán utilizadas exclusivamente con fines institucionales, académicos, periodísticos y promocionales a través de redes sociales, sitio web y material impreso, sin que esto implique derecho a compensación o retribución económica alguna.</li>
                <li>Los datos de contacto proporcionados podrán ser utilizados para el envío de los certificados de asistencia correspondientes y para comunicaciones oficiales sobre futuras ediciones del congreso.</li>
            </ul>

            <p className="font-bold text-base mt-4">6. Responsabilidad Civil</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La organización no se hará responsable por la pérdida, hurto, robo o daño de objetos personales (dispositivos electrónicos, indumentaria, mochilas) que ocurran dentro del predio durante el desarrollo del congreso.</li>
                <li>El Asistente asume total responsabilidad por su propia seguridad física y la de sus pertenencias.</li>
            </ul>

            <p className="font-bold text-base mt-4">7. Modificaciones y Cancelación</p>
            <p>La Organización del Congreso se reserva el derecho de modificar el programa, horarios, ubicación de salas, disertantes o proceder a la cancelación y reprogramación del evento por razones operativas, climáticas o de fuerza mayor, informando dichos cambios a través de los canales oficiales y correo electrónico registrado.</p>

            <p className="font-bold text-base mt-4">8. Aceptación</p>
            <p>El completamiento del formulario de inscripción y la marcación de la casilla correspondiente implica el conocimiento y aceptación plena y sin reservas de todos los puntos detallados en las presentes Bases y Condiciones.</p>
        </>
    );
}

function StandTerms() {
    return (
        <>
            <p className="font-bold text-base">1. Objeto</p>
            <p>El presente documento regula la participación de empresas expositoras mediante la contratación de stands en el Congreso de Logística y Transporte 2026, a realizarse el día sábado 7 de noviembre de 2026.</p>

            <p className="font-bold text-base mt-4">2. Asignación y Confirmación del Stand</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La asignación de espacios se realizará según disponibilidad y criterio organizativo.</li>
                <li>La confirmación oficial del stand asignado será notificada a la empresa expositora vía correo electrónico.</li>
                <li>La organización se reserva el derecho de reubicar stands por razones operativas, técnicas o de fuerza mayor.</li>
            </ul>

            <p className="font-bold text-base mt-4">3. Espacios y Medidas</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Cada stand tendrá una dimensión estándar de 3 metros x 3 metros (3x3). El expositor deberá respetar estrictamente los límites físicos del espacio asignado, sin exceder las medidas establecidas.</li>
                <li>No se permitirá ocupar pasillos ni áreas comunes con estructuras, banners, mobiliario o material promocional.</li>
                <li>Cualquier intervención estructural adicional deberá ser previamente autorizada por la organización.</li>
            </ul>

            <p className="font-bold text-base mt-4">4. Montaje y Desmontaje</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>El montaje deberá realizarse dentro del horario establecido por la organización.</li>
                <li>Las empresas expositoras deberán respetar estrictamente los horarios establecidos para montaje, ingreso de personal, apertura al público y desmontaje.</li>
                <li>No se permitirá el armado fuera del horario asignado. El desmontaje anticipado, antes del horario oficial de cierre del evento, no estará permitido bajo ninguna circunstancia.</li>
                <li>El expositor se compromete a dejar el espacio en las mismas condiciones en que fue entregado.</li>
            </ul>

            <p className="font-bold text-base mt-4">5. Compromiso de Participación</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La empresa expositora, una vez confirmada su participación, asume el compromiso de asistir y participar activamente en el evento.</li>
                <li>No podrá desistir de su participación sin causa de fuerza mayor debidamente justificada y comunicada con la debida antelación.</li>
                <li>La baja unilateral e injustificada podrá ser considerada por la organización al momento de evaluar su participación en futuras ediciones.</li>
            </ul>

            <p className="font-bold text-base mt-4">6. Equipamiento y Electricidad</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Cada stand contará con conexión eléctrica básica destinada a la alimentación de dispositivos como televisión o computadora.</li>
                <li>Las empresas expositoras deberán traer su propio alargue o prolongador eléctrico en caso de necesitar extender la conexión dentro del espacio asignado.</li>
                <li>En caso de solicitar mesa, la empresa deberá traer su propia mantelería.</li>
                <li>No se permitirá realizar instalaciones eléctricas adicionales sin autorización previa.</li>
            </ul>

            <p className="font-bold text-base mt-4">7. Acciones de Difusión y Activaciones</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La organización incentiva a las empresas expositoras a desarrollar acciones de difusión, activaciones y/o sorteos dentro de su stand, con el objetivo de generar mayor interacción con los visitantes y potenciar su presencia en el evento.</li>
                <li>Toda actividad deberá desarrollarse dentro del espacio asignado y respetando las presentes Bases y Condiciones, procurando no interferir con la dinámica general del evento.</li>
            </ul>

            <p className="font-bold text-base mt-4">8. Normas de Seguridad</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Está prohibido el uso de materiales inflamables o instalaciones eléctricas no autorizadas.</li>
                <li>El expositor es responsable por los elementos exhibidos en su stand.</li>
                <li>La organización no se responsabiliza por pérdidas, robos o daños.</li>
            </ul>

            <p className="font-bold text-base mt-4">9. Publicidad y Promoción</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Se permite la distribución de material promocional únicamente dentro del espacio asignado.</li>
                <li>No está permitido realizar acciones promocionales en pasillos o sectores comunes sin autorización previa.</li>
                <li>El uso de sonido propio deberá contar con aprobación de la organización.</li>
            </ul>

            <p className="font-bold text-base mt-4">10. Derechos de Imagen</p>
            <p>La empresa expositora autoriza a la organización a utilizar imágenes y videos del stand con fines promocionales y de difusión institucional.</p>

            <p className="font-bold text-base mt-4">11. Protección de Datos Personales</p>
            <p>Los datos provistos serán tratados con estricta confidencialidad bajo la Ley N° 25.326. La organización utilizará esta información únicamente para fines comunicacionales, logísticos y organizativos vinculados a las actividades del Congreso.</p>

            <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-4">
                <p className="font-bold text-base text-amber-900">12. Costo Operativo de Participación</p>
                <p className="mt-2 text-amber-800">
                    Se establece un costo operativo de <strong>$80.000 (pesos ochenta mil)</strong> por cada módulo de stand de 3×3 metros.
                    Este importe tiene como finalidad cubrir gastos mínimos de organización y montaje.
                </p>
                <p className="mt-3 font-semibold text-amber-900">El módulo incluye:</p>
                <ul className="mt-1 list-disc pl-5 space-y-1 text-amber-800">
                    <li>Gazebo estructural.</li>
                    <li>Una (1) mesa.</li>
                    <li>Dos (2) sillas.</li>
                    <li>Provisión de electricidad para PC o TV (uso básico, destinado a pequeños consumos).</li>
                    <li>Cartel personalizado identificatorio para el gazebo.</li>
                    <li>Credenciales para los expositores.</li>
                </ul>
            </div>

            <p className="font-bold text-base mt-4">13. Aceptación</p>
            <p>La participación en el evento implica la aceptación total de las presentes Bases y Condiciones.</p>
        </>
    );
}

function DisertanteTerms() {
    return (
        <>
            <p className="font-bold text-base">1. Objetivo</p>
            <p>El presente documento establece las condiciones generales para la participación de disertantes en el Congreso de Logística y Transporte 2026, que se llevará a cabo el día sábado 7 de noviembre de 2026.</p>

            <p className="font-bold text-base mt-4">2. Postulación</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Los interesados deberán completar el formulario oficial de inscripción.</li>
                <li>Deberán presentar título de la charla, breve resumen (máx. 300 palabras) y perfil profesional del expositor.</li>
                <li>La organización evaluará las propuestas en función de su relevancia, actualidad e impacto en el sector logístico y de transporte.</li>
            </ul>

            <p className="font-bold text-base mt-4">3. Selección</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>La confirmación como disertante será comunicada por correo electrónico.</li>
                <li>La organización se reserva el derecho de seleccionar, reprogramar o rechazar propuestas según criterios académicos y organizativos.</li>
            </ul>

            <p className="font-bold text-base mt-4">4. Modalidad de Participación</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Las exposiciones tendrán una duración estimada de 30 minutos (incluyendo preguntas).</li>
                <li>El formato podrá ser conferencia, panel o entrevista, según lo determine la organización.</li>
                <li>El disertante deberá respetar los tiempos asignados.</li>
            </ul>

            <p className="font-bold text-base mt-4">5. Contenido</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>Las presentaciones deberán ser de carácter técnico, académico o profesional.</li>
                <li>No se permitirá contenido exclusivamente comercial o promocional.</li>
                <li>El material presentado deberá respetar derechos de autor y propiedad intelectual.</li>
            </ul>

            <p className="font-bold text-base mt-4">6. Material Técnico</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>El disertante deberá enviar su presentación en formato digital hasta 7 días antes del evento.</li>
                <li>La organización proveerá proyector, sonido y equipamiento básico.</li>
                <li>Cualquier requerimiento técnico especial deberá informarse con anticipación.</li>
            </ul>

            <p className="font-bold text-base mt-4">7. Derechos de Imagen</p>
            <p>El disertante autoriza a la organización a registrar y difundir imágenes, audios y videos de su participación con fines institucionales y de difusión del evento, sin compensación económica adicional.</p>

            <p className="font-bold text-base mt-4">8. Cancelaciones</p>
            <ul className="list-disc pl-5 space-y-2">
                <li>En caso de no poder asistir, el disertante deberá informar con al menos 10 días de anticipación.</li>
                <li>La organización podrá modificar la programación por razones de fuerza mayor.</li>
            </ul>

            <p className="font-bold text-base mt-4">9. Aceptación</p>
            <p>La postulación implica la aceptación total de las presentes Bases y Condiciones.</p>

            <p className="font-bold text-base mt-4">10. Protección de Datos Personales</p>
            <p>Los datos provistos serán tratados con estricta confidencialidad bajo la Ley N° 25.326. La organización utilizará esta información únicamente para fines comunicacionales, logísticos y organizativos vinculados a las actividades del Congreso.</p>
        </>
    );
}
