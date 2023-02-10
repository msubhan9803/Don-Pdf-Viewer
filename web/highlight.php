<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  // process the form data here
  $file = $_FILES['file'];
  $summary_list = $_POST["summaryList"];
  $curl = curl_init();

  curl_setopt($curl, CURLOPT_URL, 'http://18.136.213.149/upload');
  curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl, CURLOPT_POST, true);
  curl_setopt($curl, CURLOPT_POSTFIELDS, array('file' => new \CURLFile($file['tmp_name'], $file['type'], $file['name']), 'summaryList' => $summary_list));

  $headers = [
    "Content-Type: multipart/form-data",
  ];
  curl_setopt($curl, CURLOPT_HTTPHEADER, $headers);

  $response = curl_exec($curl);
  curl_close($curl);

  echo $response;
}

// var_dump($data);

?>