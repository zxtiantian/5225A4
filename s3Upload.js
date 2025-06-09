import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const REGION = 'us-east-1'; // 替换为你的region
const BUCKET = 'bird-recognition-files';
const API_BASE = 'https://wm33a945l9.execute-api.us-east-1.amazonaws.com';

// 获取 STS 临时凭证
export async function getStsCredentials() {
  // 直接返回硬编码的临时凭证
  return {
    accessKeyId: 'ASIATLAZY4ODSTJNG75L',
    secretAccessKey: 'OVl+HGyI50gl9ldGGFmYhuI4vsuHctaC/xK79/iJ',
    sessionToken: 'IQoJb3JpZ2luX2VjEM3//////////wEaCXVzLXdlc3QtMiJGMEQCIHfJNm8Q5sy/phWBGOjTWTC2LhfETZ7MO6gnbk/5Drm3AiAczNugytNPii6I+t1VQaIHYQGL+xnoluAcscFd+IPCmyq+Agim//////////8BEAAaDDIyOTgzNDgxMDI0NyIMTbUgDMIUIOoYZ5F6KpICQfi0UGtk9i1WRmU5Xy2hMXIEBdJkRWZ/8Cz9uD55nSOw9GYWz9VPQMvTTSNM9p4hYZLSQoBx0xGyDeoQ4ZZPqbog1Lu7ojIbwT0MUAEf+FKz08m4WBkxllRel3Wo+uXjhM0CPqf/k4e/UnsXTguV1po6n9aRHqrM9DcNJrTnVTDqcSF0hupgAWdggN7RuT6jrOSwoJbatEV3lwmHrmpKQAitsD/SZ5ygem6/r78och4HCms0NZl2INpbpL0BN64WZCZrhLwpJxG2FoQkxrakHwDROpWGNIrKfmtxK4ycCU/d4d7Y70dA7Ff0TKkdHE3Wx67wU6hf3/0cYjAT9m0NHjdiyQIqJg+wnBxrY5vznnw81jC8sJvCBjqeAazUm7dvJRpyjcf61Vb+2UN1J/7TzsJfvLZWYAoCHetOrzl985L42HgOhXHb8l2S/0Cbw0J56HU446m9OpUNkLMBZXiN6xFghYb8vjPPEqhFA6fqKqls5+te07fhOt+VZnp3fNrhhIr+bqvsTG6rVMe6FWiLzUf5TYbU7ZguQuzrg4atPqqSwU6HCYVXxmHIEPWwDAkHyl+SiDV/Zop2'
  };
}

export async function uploadToS3({ file, key }) {
  // 用 ArrayBuffer 兜底，彻底规避 readableStream.getReader 报错
  const arrayBuffer = await file.arrayBuffer();
  const creds = await getStsCredentials();
  const s3 = new S3Client({
    region: REGION,
    credentials: {
      accessKeyId: creds.accessKeyId,
      secretAccessKey: creds.secretAccessKey,
      sessionToken: creds.sessionToken
    }
  });
  // 根据文件扩展名判断 Content-Type
  let contentType = file.type || 'application/octet-stream';
  const ext = key.split('.').pop().toLowerCase();
  if (["mp4", "avi", "mov", "mkv", "webm"].includes(ext)) {
    contentType = 'video/mp4';
  } else if (["mp3", "wav"].includes(ext)) {
    contentType = `audio/${ext}`;
  }
  const params = {
    Bucket: BUCKET,
    Key: key,
    Body: arrayBuffer,
    ContentType: contentType
  };
  return s3.send(new PutObjectCommand(params));
} 